import os
import subprocess
import requests
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# URL ke file VERSION di repositori GitHub Anda
GITHUB_URL = "https://raw.githubusercontent.com/fahrulariza/openwrt-telegrambot/master/VERSION"
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
VERSION_FILE_PATH = os.path.join(SCRIPT_DIR, 'VERSION')

def get_local_version():
    """Mendapatkan versi lokal dari file VERSION."""
    try:
        with open(VERSION_FILE_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0"

def get_remote_version():
    """Mendapatkan versi terbaru dari GitHub."""
    try:
        response = requests.get(GITHUB_URL)
        response.raise_for_status()  # Angkat pengecualian untuk kode status HTTP yang buruk
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal mendapatkan versi remote: {e}")
        return None

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    """Menangani perintah update."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    # Notifikasi bahwa proses sedang berjalan
    await context.bot.send_message(chat_id=chat_id, text="🔍 Sedang memeriksa pembaruan...")

    local_version = get_local_version()
    remote_version = get_remote_version()

    if not remote_version:
        await context.bot.send_message(chat_id=chat_id, text="❌ Gagal memeriksa pembaruan. Tidak dapat terhubung ke GitHub.")
        return

    if remote_version == local_version:
        await context.bot.send_message(chat_id=chat_id, text=f"🎉 Versi sudah terbaru. Saat ini v{local_version}.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Pembaruan baru tersedia! (v{local_version} -> v{remote_version}).\n\nSedang mengunduh dan memasang...")
        
        # Logika untuk mengunduh dan memasang pembaruan
        try:
            subprocess.run(['/www/assisten/bot/update.sh'], check=True, capture_output=True)
            await context.bot.send_message(chat_id=chat_id, text="✅ Pembaruan berhasil dipasang. Bot akan segera dimulai ulang.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Gagal menjalankan skrip pembaruan: {e.stderr.decode().strip()}")
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Gagal memasang pembaruan: {e.stderr.decode().strip()}")
        except Exception as e:
            logger.error(f"Kesalahan tak terduga saat memasang pembaruan: {e}")
            await context.bot.send_message(chat_id=chat_id, text="❌ Terjadi kesalahan saat memasang pembaruan.")

    # Menghapus pesan tombol setelah selesai
    try:
        await query.message.delete()
    except Exception:
        pass
