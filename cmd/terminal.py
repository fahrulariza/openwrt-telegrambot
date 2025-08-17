import subprocess
import logging
import asyncio
import shlex  # Digunakan untuk memecah string perintah dengan aman
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengeksekusi perintah terminal dengan parameter aman dan mengirim hasilnya."""
    
    command_str = " ".join(context.args)

    if not command_str:
        await update.message.reply_text("Mohon sertakan perintah terminal. Contoh: `/terminal ps`", parse_mode='Markdown')
        return

    # --- Logika Otomatisasi Perintah ---
    original_command = command_str
    
    # Gunakan shlex untuk memecah perintah dengan aman
    command_parts = shlex.split(command_str)
    base_command = command_parts[0]
    args = command_parts[1:]
    
    if base_command == 'ping':
        if '-c' not in args and '--count' not in args:
            args.extend(['-c', '4'])
            command_str = f"{base_command} {' '.join(args)}"
            await update.message.reply_text("ℹ️ Perintah 'ping' dimodifikasi menjadi 4 paket untuk menghindari bot macet.", parse_mode='Markdown')
    elif base_command == 'top':
        if '-b' not in args and '-n' not in args:
            args.extend(['-b', '-n', '1'])
            command_str = f"{base_command} {' '.join(args)}"
            await update.message.reply_text("ℹ️ Perintah 'top' dimodifikasi untuk menampilkan satu iterasi.", parse_mode='Markdown')
    elif base_command == 'tail':
        if '-f' in args:
            args.remove('-f')
            command_str = f"{base_command} {' '.join(args)}"
            await update.message.reply_text("ℹ️ Opsi 'tail -f' dihapus untuk menghindari bot macet.", parse_mode='Markdown')
    elif base_command == 'traceroute':
        if '-m' not in args:
            args.extend(['-n', '-m', '5'])
            command_str = f"{base_command} {' '.join(args)}"
            await update.message.reply_text("ℹ️ Perintah 'traceroute' dimodifikasi untuk 5 hop dan tanpa DNS lookup.", parse_mode='Markdown')

    try:
        process = await asyncio.create_subprocess_shell(
            command_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        output = stdout.decode('utf-8').strip()
        error = stderr.decode('utf-8').strip()

        response = ""
        if output:
            response += f"```\n{output}\n```"
        else:
            response += "✅ Perintah berhasil dieksekusi, tetapi tidak ada output."
        
        if error:
            response += f"\n\n❌ Error:\n```\n{error}\n```"

        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengeksekusi perintah. Error: {e}")
        logger.error(f"Gagal mengeksekusi perintah '{original_command}': {e}")
