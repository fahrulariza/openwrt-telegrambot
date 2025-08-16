import os
import logging
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Message

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Menangani perintah /update.
    Fungsi ini menampilkan versi lokal dan versi GitHub dan
    menawarkan tombol untuk pembaruan jika versi baru tersedia.
    """
    
    chat_id = update.effective_chat.id
    SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Panggil skrip update.sh untuk mendapatkan status versi
        process = await asyncio.create_subprocess_exec(
            '/bin/sh', os.path.join(SCRIPT_DIR, 'update.sh'), '--check',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode('utf-8').strip()
        
        # Pisahkan output menjadi baris dan cari versi
        lines = output.split('\n')
        local_version = "Tidak terdeteksi"
        github_version = "Tidak terdeteksi"
        
        for line in lines:
            if "Versi lokal:" in line:
                local_version = line.split(':')[1].strip()
            elif "Versi GitHub:" in line:
                github_version = line.split(':')[1].strip()
        
        message_text = f"⚙️ **Status Pembaruan**\n"
        message_text += f"Versi Lokal: `{local_version}`\n"
        message_text += f"Versi GitHub: `{github_version}`\n"
        
        keyboard = []
        if local_version != "Tidak terdeteksi" and github_version != "Tidak terdeteksi" and local_version != github_version:
            message_text += "Pembaruan tersedia! Silakan klik tombol di bawah untuk menginstal."
            keyboard.append([InlineKeyboardButton("Install Update", callback_data="install_update")])
        else:
            message_text += "Anda sudah menggunakan versi terbaru."
            
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"Status pembaruan berhasil dikirim ke chat ID {chat_id}.")
        
    except Exception as e:
        logger.error(f"Gagal menjalankan pemeriksaan pembaruan: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Maaf, terjadi kesalahan saat memeriksa pembaruan."
        )
