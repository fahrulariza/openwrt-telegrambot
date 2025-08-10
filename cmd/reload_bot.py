import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    chat_id = update.effective_chat.id

    # Ambil selected_device dari command_data
    command_parts = command_data.split('|')
    selected_device = command_parts[2]

    if selected_device == os.getenv('DEVICE_ID'):
        await context.bot.send_message(chat_id=chat_id, text="Memulai proses restart bot...")

        # Panggil run_bot.sh dengan argumen 'stop' lalu 'start'
        try:
            subprocess.run(['/www/assisten/bot/run_bot.sh', 'stop'], check=True)
            await context.bot.send_message(chat_id=chat_id, text="Proses bot.py berhasil dihentikan. run_bot.sh akan memulai ulang bot secara otomatis.")
            subprocess.Popen(['/www/assisten/bot/run_bot.sh', 'start'])
        except FileNotFoundError:
            await context.bot.send_message(chat_id=chat_id, text="❌ Gagal: File run_bot.sh tidak ditemukan.")
        except subprocess.CalledProcessError as e:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Gagal: Terjadi error saat menjalankan run_bot.sh: {e}")
    else:
        logger.info("Perintah /reload_bot diabaikan karena tidak cocok dengan DEVICE_ID.")
        await context.bot.send_message(chat_id=chat_id, text="Perintah ini hanya dapat dijalankan di perangkat yang aktif.")
