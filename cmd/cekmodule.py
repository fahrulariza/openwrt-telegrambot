import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

# Tambahkan baris ini
IS_MENU_COMMAND = True

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan daftar semua modul yang dimuat."""
    
    # Periksa apakah ada modul yang dimuat
    if not context.application.bot_data.get('menu_commands') and not context.application.bot_data.get('hidden_commands'):
        await update.message.reply_text("❌ Tidak ada modul yang terdeteksi.")
        return

    # Kumpulkan daftar semua modul yang dimuat
    all_modules = {**context.application.bot_data.get('menu_commands', {}), **context.application.bot_data.get('hidden_commands', {})}
    sorted_module_names = sorted(all_modules.keys())

    response = "📜 **Daftar Modul yang Dimuat:**\n\n"
    
    for module_name in sorted_module_names:
        module = all_modules[module_name]
        
        # Ambil informasi versi (default: 'Tidak ada')
        version = getattr(module, 'VERSION', 'Tidak ada')
        
        # Ambil status menu (default: True)
        is_menu_command = getattr(module, 'IS_MENU_COMMAND', True)
        status = "MENU" if is_menu_command else "TEKS"
        
        response += f"• **{module_name.capitalize()}** (v{version}) - `{status}`\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')
