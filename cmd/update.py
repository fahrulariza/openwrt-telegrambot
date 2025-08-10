import os
import subprocess
import requests
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# URL ke file VERSION di repositori GitHub Anda (pastikan branch sudah 'master')
GITHUB_URL = "https://raw.githubusercontent.com/fahrulariza/openwrt-telegrambot/master/VERSION"
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
VERSION_FILE_PATH = os.path.join(SCRIPT_DIR, 'VERSION')

def get_local_version():
    """Mendapatkan versi lokal dari file VERSION."""
    try:
        with open(VERSION_FILE_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "v0.0"

def get_remote_version():
    """Mendapatkan versi terbaru dari GitHub."""
    try:
        response = requests.get(GITHUB_URL, timeout=10) # Tambahkan timeout
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal mendapatkan versi remote: {e}")
        return None

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    """Menangani perintah update."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(chat_id=chat_id, text="🔍 Sedang memeriksa pembaruan...")

    local_version = get_local_version()
    remote_version = get_remote_version()

    if not remote_version:
        await context.bot.send_message(chat_id=chat_id, text="❌ Gagal memeriksa pembaruan. Tidak dapat terhubung ke GitHub.")
        return

    if remote_version == local_version:
        await context.bot.send_message(chat_id=chat_id, text=f"🎉 Versi sudah terbaru. Saat ini {local_version}.")
    else:
        keyboard = [[InlineKeyboardButton("Pasang Pembaruan", callback_data=f"install_update|menu|{os.getenv('DEVICE_ID')}@{remote_version}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Pembaruan baru tersedia! ({local_version} -> {remote_version}).", reply_markup=reply_markup)

    try:
        await query.message.delete()
    except Exception:
        pass
