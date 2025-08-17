import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# versi modul
VERSION = "3.5.1"

IS_MENU_COMMAND = False

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None) -> None:
    """Menampilkan daftar semua modul yang dimuat."""
    
    if not context.application.bot_data.get('menu_commands') and not context.application.bot_data.get('hidden_commands'):
        await update.message.reply_text("❌ Tidak ada modul yang terdeteksi.")
        return

    all_modules = {
        **context.application.bot_data.get('menu_commands', {}), 
        **context.application.bot_data.get('hidden_commands', {})
    }
    sorted_module_names = sorted(all_modules.keys())

    response = "📜 *Daftar Modul yang Dimuat:*\n\n"
    
    for module_name in sorted_module_names:
        module = all_modules[module_name]
        
        version = getattr(module, 'VERSION', 'Tidak ada')
        is_menu_command = getattr(module, 'IS_MENU_COMMAND', True)
        status = "MENU" if is_menu_command else "CMD"
        
        safe_module_name = escape_markdown(module_name.capitalize(), version=2)
        safe_version = escape_markdown(str(version), version=2)
        safe_status = escape_markdown(status, version=2)

        response += f"• **{safe_module_name}** \(v{safe_version}\) \- \`{safe_status}\`\n"
    
    await update.message.reply_text(response, parse_mode='MarkdownV2')
