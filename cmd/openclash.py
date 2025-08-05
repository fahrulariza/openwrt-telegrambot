import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import subprocess
import logging

# Ganti dengan DEVICE_ID Anda
DEVICE_ID = os.environ.get('DEVICE_ID', 'rumah-menteng.net')

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Mengirim menu perintah OpenClash dan memprosesnya."""
    
    # Menentukan objek pesan yang akan digunakan
    message_obj = update.effective_message
    chat_id = message_obj.chat_id

    # Menguraikan `callback_data` dari tombol yang diklik
    if command_data:
        command_parts = command_data.split('|')
        action = command_parts[1] if len(command_parts) > 1 else 'menu'
    else:
        action = 'menu' # Jika perintah datang dari /openclash, tampilkan menu

    # Opsi perintah yang tersedia
    actions = ['status', 'start', 'stop', 'restart']
    
    if action in actions:
        # Jalankan aksi yang ditentukan
        await handle_action(update, context, action, chat_id)
    else:
        # Tampilkan menu default jika tidak ada aksi yang valid
        await send_openclash_menu(update, context, chat_id)

async def send_openclash_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Mengirim menu perintah OpenClash."""
    keyboard = [
        [InlineKeyboardButton("Status", callback_data=f"openclash|status|{DEVICE_ID}")],
        [InlineKeyboardButton("Start", callback_data=f"openclash|start|{DEVICE_ID}")],
        [InlineKeyboardButton("Stop", callback_data=f"openclash|stop|{DEVICE_ID}")],
        [InlineKeyboardButton("Restart", callback_data=f"openclash|restart|{DEVICE_ID}")],
        [InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|{DEVICE_ID}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Anda memilih OpenClash. Silakan pilih perintah:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, chat_id: int) -> None:
    """Menjalankan perintah OpenClash dan mengirim hasilnya."""
    
    command = f"/etc/init.d/openclash {action}"
    
    try:
        logging.info(f"Menjalankan perintah OpenClash: {command}")
        
        process = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        output = process.stdout.strip()

        if action == 'status':
            response_text = f"✅ Status OpenClash:\n`{output}`"
        elif action == 'start':
            response_text = f"✅ OpenClash berhasil dijalankan."
        elif action == 'stop':
            response_text = f"✅ OpenClash berhasil dihentikan."
        elif action == 'restart':
            response_text = f"✅ OpenClash berhasil dimulai ulang."
        else:
            response_text = f"✅ Perintah {action} berhasil dijalankan."
            
        keyboard = [[InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|{DEVICE_ID}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except subprocess.CalledProcessError as e:
        error_message = f"❌ Gagal menjalankan perintah OpenClash `{action}`.\nKesalahan: `{e.stderr.strip()}`"
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