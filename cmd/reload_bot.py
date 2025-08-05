import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menghentikan bot untuk memulai ulang."""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏳ Bot sedang di-restart. Mohon tunggu sebentar...lalu jalankan /start ulang",
        )
        
        # Panggil skrip shell untuk melakukan restart
        subprocess.Popen(["/www/assisten/bot/restart.sh"])

    except Exception as e:
        logger.error(f"Gagal menjalankan perintah restart: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Gagal me-restart bot. Terjadi kesalahan: `{e}`",
        )