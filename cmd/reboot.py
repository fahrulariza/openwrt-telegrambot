import os
import subprocess
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging

# versi modul
VERSION = "3.5.0"

DEVICE_ID = os.environ.get('DEVICE_ID', 'rumah-menteng.net')

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menangani perintah reboot dengan konfirmasi."""

    message_obj = update.effective_message
    chat_id = message_obj.chat_id

    # Menguraikan `callback_data` dari tombol yang diklik
    if command_data:
        command_parts = command_data.split('|')
        action = command_parts[1] if len(command_parts) > 1 else 'menu'
    else:
        action = 'menu'

    if action == 'confirm':
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔄 Perangkat sedang dimulai ulang...",
            parse_mode='Markdown'
        )
        try:
            logging.info(f"Menjalankan perintah reboot")
            subprocess.run(["/sbin/reboot"], check=True)
        except subprocess.CalledProcessError as e:
            error_message = f"❌ Gagal menjalankan perintah `reboot`.\nKesalahan: `{e.stderr.strip()}`"
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            error_message = f"❌ Terjadi kesalahan tak terduga: `{e}`"
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_message,
                parse_mode='Markdown'
            )
    else:
        keyboard = [
            [InlineKeyboardButton("✅ Ya, Reboot Sekarang", callback_data=f"reboot|confirm|{DEVICE_ID}")],
            [InlineKeyboardButton("❌ Batalkan", callback_data=f"back_to_device_menu|{DEVICE_ID}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text="❗ **Apakah Anda yakin ingin memulai ulang perangkat?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
