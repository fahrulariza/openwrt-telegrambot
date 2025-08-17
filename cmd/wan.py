import subprocess
import logging
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

IS_MENU_COMMAND = True
VERSION = "1.0.2"

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menampilkan status koneksi WAN (Internet)."""

    chat_id = update.effective_chat.id

    selected_device = None
    if command_data:
        parts = command_data.split('|')
        if len(parts) > 2:
            selected_device = parts[2]

    try:
        # Dapatkan IP Publik
        public_ip_proc = await asyncio.create_subprocess_shell(
            'curl -s ifconfig.me',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        public_ip_stdout, _ = await public_ip_proc.communicate()
        public_ip = public_ip_stdout.decode('utf-8').strip() or "Tidak terdeteksi"

        # Dapatkan IP Lokal WAN dan Antarmuka WAN
        wan_interface = "Tidak terdeteksi"
        wan_ip = "Tidak terdeteksi"
        ip_output_proc = await asyncio.create_subprocess_shell(
            'ip -4 addr show | grep -E "inet"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        ip_output_stdout, _ = await ip_output_proc.communicate()
        ip_lines = ip_output_stdout.decode('utf-8').strip().split('\n')
        for line in ip_lines:
            if "br-lan" not in line and "lo" not in line:
                parts = line.split()
                if "inet" in parts:
                    wan_ip = parts[1].split('/')[0]
                    wan_interface = parts[-1]
                    break

        # Dapatkan Gateway beserta Antarmuka
        gateway_list = []
        gateway_proc = await asyncio.create_subprocess_shell(
            'ip route | grep default',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        gateway_stdout, _ = await gateway_proc.communicate()
        gateway_lines = gateway_stdout.decode('utf-8').strip().split('\n')
        for line in gateway_lines:
            if "via" in line and "dev" in line:
                parts = line.split()
                gateway_ip = parts[parts.index("via") + 1]
                gateway_interface = parts[parts.index("dev") + 1]
                gateway_list.append(f"{gateway_interface} = {gateway_ip}")
        gateway_str = "\n".join(gateway_list) if gateway_list else "Tidak terdeteksi"

        # Dapatkan DNS berdasarkan tipe (IPv4/IPv6)
        dns_ipv4_list = []
        dns_ipv6_list = []
        dns_proc = await asyncio.create_subprocess_shell(
            'grep nameserver /etc/resolv.conf',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        dns_stdout, _ = await dns_proc.communicate()
        dns_lines = dns_stdout.decode('utf-8').strip().split('\n')
        for line in dns_lines:
            if "nameserver" in line:
                dns_ip = line.split()[1]
                if ':' in dns_ip:
                    dns_ipv6_list.append(dns_ip)
                else:
                    dns_ipv4_list.append(dns_ip)

        dns_str = ""
        if dns_ipv4_list:
            dns_str += "ipv4 = " + "\n       ".join(dns_ipv4_list) + "\n"
        if dns_ipv6_list:
            dns_str += "ipv6 = " + "\n       ".join(dns_ipv6_list) + "\n"
        dns_str = dns_str.strip() if dns_str else "Tidak terdeteksi"

        # Format respons dengan MarkdownV2
        response = (
            f"🌐 **Status WAN**\n"
            f"IP Publik: `{escape_markdown(public_ip, version=2)}`\n"
            f"IP Lokal WAN: `{escape_markdown(wan_ip, version=2)}`\n"
            f"Antarmuka WAN: `{escape_markdown(wan_interface, version=2)}`\n"
            f"Gateway:\n`{escape_markdown(gateway_str, version=2)}`\n"
            f"DNS:\n`{escape_markdown(dns_str, version=2)}`"
        )
        
        # Buat tombol Kembali
        keyboard = []
        if selected_device:
            keyboard.append([InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|menu|{selected_device}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=response,
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Gagal menjalankan perintah /wan: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Maaf, terjadi kesalahan saat mengambil status WAN."
        )
