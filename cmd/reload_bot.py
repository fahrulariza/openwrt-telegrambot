import os
import subprocess
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# versi modul
VERSION = "3.5.0"

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    chat_id = update.effective_chat.id
    
    command_parts = command_data.split('|')
    selected_device = command_parts[2]

    # Tombol "Kembali ke Menu Utama"
    keyboard = [
        [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if selected_device == os.getenv('DEVICE_ID'):
        try:
            # Hapus pesan perintah
            await update.callback_query.message.delete()
        except Exception:
            pass
            
        # Kirim pesan konfirmasi SUKSES SEBELUM bot dihentikan
        await context.bot.send_message(
            chat_id=chat_id, 
            text="✅ Berhasil me-restart bot. Bot akan kembali aktif dalam beberapa saat.",
            reply_markup=reply_markup
        )
        
        try:
            # Panggil skrip restart.sh di latar belakang
            # Ini akan memastikan bot berhenti dan memulai ulang dengan benar
            subprocess.Popen(['/bin/sh', '/www/assisten/bot/restart.sh'])
            
        except FileNotFoundError:
            await context.bot.send_message(
                chat_id=chat_id, 
                text="❌ Gagal: File restart.sh tidak ditemukan.",
                reply_markup=reply_markup
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ Gagal: Terjadi error saat menjalankan restart.sh: {e}",
                reply_markup=reply_markup
            )
    else:
        # Pesan jika perintah tidak dijalankan di perangkat yang benar
        await context.bot.send_message(
            chat_id=chat_id, 
            text="Perintah ini hanya dapat dijalankan di perangkat yang aktif.",
            reply_markup=reply_markup
        )
