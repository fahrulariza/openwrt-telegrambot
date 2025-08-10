import os
import subprocess
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    chat_id = update.effective_chat.id
    
    command_parts = command_data.split('|')
    selected_device = command_parts[2]

    if selected_device == os.getenv('DEVICE_ID'):
        try:
            # Hapus pesan perintah
            await update.callback_query.message.delete()
        except Exception:
            pass

        # Tombol "Kembali ke Menu Utama"
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Kirim pesan konfirmasi SUKSES SEBELUM bot dihentikan
        await context.bot.send_message(
            chat_id=chat_id, 
            text="✅ Berhasil me-restart bot. Bot akan kembali aktif dalam beberapa saat.",
            reply_markup=reply_markup
        )
        
        # Kirim pesan untuk log saja
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔄 Memulai proses restart bot..."
        )
        
        try:
            # Hentikan bot, Popen akan mengabaikan error
            subprocess.Popen(['/www/assisten/bot/run_bot.sh', 'stop'])
            
        except FileNotFoundError:
            logger.error("Gagal: File run_bot.sh tidak ditemukan.")
            await context.bot.send_message(
                chat_id=chat_id, 
                text="❌ Gagal: File run_bot.sh tidak ditemukan.",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Gagal: Terjadi error saat menjalankan run_bot.sh: {e}")
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ Gagal: Terjadi error saat menjalankan run_bot.sh: {e}",
                reply_markup=reply_markup
            )
    else:
        logger.info("Perintah /reload_bot diabaikan karena tidak cocok dengan DEVICE_ID.")
        # Kirim pesan dengan tombol kembali jika perintah diabaikan
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id, 
            text="Perintah ini hanya dapat dijalankan di perangkat yang aktif.",
            reply_markup=reply_markup
        )
