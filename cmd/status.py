import os
import subprocess
import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging

DEVICE_ID = os.environ.get('DEVICE_ID', 'rumah-menteng.net')

def format_memory(value_mb: str) -> str:
    """Mengonversi nilai MB ke GB jika lebih besar dari 1024 MB."""
    try:
        value_mb = int(value_mb)
        if value_mb > 1024:
            value_gb = value_mb / 1024
            return f"{value_gb:.2f} GB"
        return f"{value_mb} MB"
    except (ValueError, TypeError):
        return f"{value_mb} MB"

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menjalankan perintah 'status' dan mengirim hasilnya."""

    try:
        # Mengambil informasi CPU dari /proc/cpuinfo
        cpuinfo_output = subprocess.run(['cat', '/proc/cpuinfo'], capture_output=True, text=True, check=True).stdout.strip()
        
        cpu_model_match = re.search(r'model name\s*:\s*(.*)', cpuinfo_output)
        cpu_model = cpu_model_match.group(1).strip() if cpu_model_match else "Tidak tersedia"
        
        cores_count = len(re.findall(r'processor\s*:', cpuinfo_output))

        # Mengambil arsitektur CPU yang lebih spesifik
        try:
            arch_output = subprocess.run(['opkg', 'print-architecture'], capture_output=True, text=True, check=True).stdout.strip()
            arch_matches = re.findall(r'arch\s+((?!all|noarch)\S+)\s+\d+', arch_output)
            cpu_arch = arch_matches[0] if arch_matches else "Tidak tersedia"
        except (subprocess.CalledProcessError, FileNotFoundError):
            cpu_arch = "Tidak tersedia"

        # Mengambil informasi uptime dan load average
        uptime_command = 'uptime'
        uptime_output = subprocess.run(uptime_command, shell=True, capture_output=True, text=True, check=True).stdout.strip()
        
        uptime_match = re.search(r'up\s+((?P<days>\d+)\s+days,\s+)?((?P<hours>\d+):(?P<minutes>\d+)|(?P<single_hour>\d+)\s+min)', uptime_output)
        
        if uptime_match:
            days = int(uptime_match.group('days') or 0)
            hours = int(uptime_match.group('hours') or 0)
            minutes = int(uptime_match.group('minutes') or 0)
            
            uptime_str = []
            if days > 0: uptime_str.append(f"{days}d")
            if hours > 0 or days > 0: uptime_str.append(f"{hours}h")
            uptime_str.append(f"{minutes}m")
            uptime_str = ' '.join(uptime_str)
        else:
            uptime_str = "Tidak tersedia"
        
        load_avg = ','.join([p.strip() for p in uptime_output.split(',')[1:]]).strip()

        # Mengambil informasi memori dalam MB
        mem_command = 'free -m'
        mem_output = subprocess.run(mem_command, shell=True, capture_output=True, text=True, check=True).stdout.strip()
        mem_lines = mem_output.split('\n')
        mem_info = mem_lines[1].split()
        mem_total = format_memory(mem_info[1])
        mem_used = format_memory(mem_info[2])
        mem_free = format_memory(mem_info[3])

        swap_info = mem_lines[2].split()
        swap_total = format_memory(swap_info[1])
        swap_used = format_memory(swap_info[2])

        # Mengambil informasi penyimpanan
        storage_command = 'df -h /'
        storage_output = subprocess.run(storage_command, shell=True, capture_output=True, text=True, check=True).stdout.strip().split('\n')[1].split()
        storage_total = storage_output[1]
        storage_used = storage_output[2]
        storage_avail = storage_output[3]
        storage_used_percent = storage_output[4]
        
        # Mengambil informasi suhu CPU (jika tersedia)
        cpu_temp = "Tidak tersedia."
        temp_file_path = '/sys/class/thermal/thermal_zone0/temp'
        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'r') as f:
                temp_raw = f.read().strip()
                cpu_temp = f"{int(temp_raw) / 1000:.1f}°C"

        # Mengambil informasi GPU (jika tersedia)
        gpu_info = "Tidak tersedia."
        if os.path.exists('/dev/dri'):
            gpu_info = "Terdeteksi."
        
        # Mengambil informasi versi OpenWrt (jika tersedia)
        version = "Tidak tersedia."
        version_file_path = '/etc/openwrt_release'
        if os.path.exists(version_file_path):
            with open(version_file_path, 'r') as f:
                for line in f.readlines():
                    if line.startswith('DISTRIB_DESCRIPTION'):
                        version = line.split('=')[1].strip().replace("'", "")
                        break
        
        # Membuat string respons yang rapi menggunakan DEVICE_ID
        response_text = (
            f"✅ *Status Perangkat ({DEVICE_ID})*\n\n"
            f"**Informasi Umum**\n"
            f"• Versi: `{version}`\n"
            f"• Uptime: `{uptime_str}`\n"
            f"• Suhu: `{cpu_temp}`\n\n"
            f"**CPU**\n"
            f"• Model: `{cpu_model}`\n"
            f"• Arsitektur: `{cpu_arch}`\n"
            f"• Core: `{cores_count}`\n"
            f"• Beban Rata-rata: `{load_avg}`\n\n"
            f"**Memori (RAM)**\n"
            f"• Total: `{mem_total}`\n"
            f"• Digunakan: `{mem_used}`\n"
            f"• Tersedia: `{mem_free}`\n\n"
            f"**Penyimpanan**\n"
            f"• Total: `{storage_total}`\n"
            f"• Digunakan: `{storage_used} ({storage_used_percent})`\n"
            f"• Tersedia: `{storage_avail}`\n\n"
            f"**GPU**\n"
            f"• Status: `{gpu_info}`"
        )

        keyboard = [[InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|{DEVICE_ID}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    except subprocess.CalledProcessError as e:
        error_message = f"❌ Gagal menjalankan perintah `status`.\nKesalahan: `{e.stderr.strip()}`"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message,
            parse_mode='Markdown'
        )
    except Exception as e:
        error_message = f"❌ Terjadi kesalahan tak terduga: `{e}`"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message,
            parse_mode='Markdown'
        )