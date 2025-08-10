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
        return "v0.0"

def get_remote_version():
    """Mendapatkan versi terbaru dari GitHub."""
    try:
        response = requests.get(GITHUB_URL, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal mendapatkan versi remote: {e}")
        return None

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    """Menangani perintah update."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    # Perintah /update tidak membutuhkan pesan awal, karena update handler di bot.py
    # sudah mengirimkan pesan "Mencari pembaruan..."
    # await context.bot.send_message(chat_id=chat_id, text="🔍 Sedang memeriksa pembaruan...")

    local_version = get_local_version()
    remote_version = get_remote_version()
    
    # Ambil selected_device dari command_data
    command_parts = command_data.split('|')
    selected_device = command_parts[2]

    # Tombol "Kembali" untuk menu perintah perangkat
    back_to_device_menu_button = [InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|{selected_device}")]
    
    # Tangani pesan error
    if not remote_version:
        keyboard = [back_to_device_menu_button]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id, 
            text="❌ Gagal memeriksa pembaruan. Tidak dapat terhubung ke GitHub.",
            reply_markup=reply_markup
        )
        return

    # Respons jika versi sudah terbaru
    if remote_version == local_version:
        keyboard = [back_to_device_menu_button]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"🎉 Versi sudah terbaru. Saat ini {local_version}.",
            reply_markup=reply_markup
        )
    # Respons jika ada pembaruan
    else:
        keyboard = [
            [InlineKeyboardButton("Pasang Pembaruan", callback_data=f"install_update|menu|{selected_device}")],
            back_to_device_menu_button
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"✅ Pembaruan baru tersedia! ({local_version} -> {remote_version}).", 
            reply_markup=reply_markup
        )

    # Hapus pesan perintah sebelumnya (jika ada)
    try:
        await query.message.delete()
    except Exception:
        pass