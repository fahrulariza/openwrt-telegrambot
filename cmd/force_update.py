# File: cmd/force_update.py

import os
import logging
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Lokasi skrip force_update.sh
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORCE_UPDATE_SCRIPT = os.path.join(SCRIPT_DIR, "force_update.sh")

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menangani perintah /force_update untuk memaksa pembaruan."""
    
    chat_id = update.effective_chat.id
    
    # Kirim pesan notifikasi
    message = "🚨 **Memaksa pembaruan perangkat saat ini...**"
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown'
    )
    logger.info("Perintah /force_update diterima. Memulai skrip pembaruan paksa.")

    # Jalankan skrip force_update.sh secara asinkron
    subprocess.Popen(['/bin/sh', FORCE_UPDATE_SCRIPT])
    
    # Hapus baris ini:
    # await context.application.stop()
