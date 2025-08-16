import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Ubah definisi fungsi execute() untuk menerima argumen opsional
async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menangani perintah /force_update untuk memaksa pembaruan di semua perangkat."""
    
    chat_id = update.effective_chat.id
    
    # Kirim pesan notifikasi kepada pengguna
    message = "🚨 **Memaksa pembaruan di semua perangkat...**"
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown'
    )
    logger.info("Perintah /force_update diterima. Mengirim sinyal pembaruan paksa ke semua perangkat.")

    # Kirim pesan khusus ke semua chat utama
    # Pesan ini akan ditangani oleh `reload_handler` di bot.py
    if 'main_chat_ids' in context.application.bot_data:
        for target_chat_id in context.application.bot_data['main_chat_ids']:
            await context.bot.send_message(
                chat_id=target_chat_id,
                text="RELOAD|ALL",
                disable_notification=True,
                disable_web_page_preview=True
            )
