import os
import sys
import datetime
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import ContextTypes

# versi modul
VERSION = "3.5.0"

logger = logging.getLogger(__name__)

# Konfigurasi file akses
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AKSES_FILE = os.path.join(SCRIPT_DIR, "akses.txt")
AKSES_EDIT_FILE = os.path.join(SCRIPT_DIR, "akses.txt.tmp")

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str) -> None:
    """Fungsi utama untuk mengelola user yang diizinkan."""
    query = update.callback_query
    
    command_parts = command_data.split('|')
    action = command_parts[0] if len(command_parts) > 0 else 'akses'
    sub_action = command_parts[1] if len(command_parts) > 1 else 'menu'
    selected_device = command_parts[2] if len(command_parts) > 2 else 'local'

    if sub_action == 'menu':
        try:
            return await show_access_menu(update, context, selected_device)
        except Exception:
            try: await query.message.delete()
            except Exception: pass
            return await show_access_menu(update, context, selected_device, new_message=True)
    elif sub_action == 'view':
        try:
            return await view_users(update, context, selected_device)
        except Exception:
            try: await query.message.delete()
            except Exception: pass
            return await view_users(update, context, selected_device, new_message=True)
    elif sub_action == 'add_self':
        return await add_user(update, context, selected_device)
    elif sub_action == 'add_manual':
        return await add_user_prompt(update, context, selected_device)
    elif sub_action == 'del_user':
        user_id_to_del = command_parts[3]
        return await delete_user(update, context, user_id_to_del, selected_device)
    elif sub_action == 'back':
        # Mengimpor modul bot secara lokal untuk menghindari kesalahan saat import di cmd
        from bot import send_device_menu
        try: await query.message.delete()
        except Exception: pass
        return await send_device_menu(update, context, selected_device)
    return

async def show_access_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_device: str, new_message=False):
    """Menampilkan menu untuk mengelola user yang diizinkan."""
    keyboard = [
        [InlineKeyboardButton("Lihat User", callback_data=f"akses|view|{selected_device}")],
        [InlineKeyboardButton("Tambah User Saat Ini", callback_data=f"akses|add_self|{selected_device}")],
        [InlineKeyboardButton("Tambah User Manual", callback_data=f"akses|add_manual|{selected_device}")],
        [InlineKeyboardButton("Kembali", callback_data=f"back_to_device_menu|{selected_device}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query and not new_message:
            message = await update.callback_query.message.edit_text(
                "Pilih opsi manajemen user:",
                reply_markup=reply_markup
            )
        else:
            message = await update.effective_message.reply_text(
                "Pilih opsi manajemen user:",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Gagal menampilkan menu akses: {e}")
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Pilih opsi manajemen user:",
            reply_markup=reply_markup
        )
    return message

async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_device: str, new_message=False):
    """Membaca dan menampilkan daftar user yang diizinkan, dengan tombol hapus."""
    try:
        with open(AKSES_FILE, 'r') as f:
            users = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        keyboard = []
        if users:
            response_text = "Daftar User yang Diizinkan:"
            for user_id_str in users:
                user_id = int(user_id_str)
                if user_id != update.effective_user.id:
                    keyboard.append(
                        [InlineKeyboardButton(f"Hapus User ID {user_id}", callback_data=f"akses|del_user|{selected_device}|{user_id_str}")]
                    )
                else:
                    keyboard.append(
                        [InlineKeyboardButton(f"User ID {user_id} (Anda)", callback_data=f"ignore_self")]
                    )
        else:
            response_text = "Tidak ada user yang terdaftar."
        
        keyboard.append([InlineKeyboardButton("Kembali", callback_data=f"akses|menu|{selected_device}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

    except FileNotFoundError:
        response_text = f"File `{AKSES_FILE}` tidak ditemukan."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data=f"akses|menu|{selected_device}")]])
    
    try:
        if update.callback_query and not new_message:
            message = await update.callback_query.message.edit_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            message = await update.effective_message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Gagal menampilkan daftar user: {e}")
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    return message

async def add_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_device: str):
    """Meminta user ID untuk ditambahkan secara manual."""
    try:
        await update.callback_query.message.delete()
    except Exception:
        pass

    keyboard = [[InlineKeyboardButton("Kembali", callback_data=f"akses|menu|{selected_device}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['state'] = 'await_add_user_id'
    context.user_data['selected_device'] = selected_device

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Kirimkan user ID yang ingin Anda tambahkan (contoh: 1234567890).",
        reply_markup=reply_markup
    )
    return message

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani input teks dari user, khususnya untuk menambah user ID."""
    if 'state' in context.user_data and context.user_data['state'] == 'await_add_user_id':
        user_input = update.message.text
        
        try:
            if not user_input.isdigit():
                raise ValueError("Input harus berupa angka.")

            user_id = int(user_input)
            
            selected_device = context.user_data.get('selected_device', 'local')
            
            del context.user_data['state']
            if 'selected_device' in context.user_data:
                del context.user_data['selected_device']

            with open(AKSES_FILE, 'r+') as f:
                content = f.read()
                if str(user_id) in [line.strip() for line in content.splitlines()]:
                    response_text = f"✅ User ID `{user_id}` sudah ada."
                else:
                    f.write(f"\n{user_id}")
                    response_text = f"✅ User ID `{user_id}` berhasil ditambahkan."
                    
            from bot import load_allowed_users
            load_allowed_users()
            
        except ValueError as e:
            response_text = f"❌ Input `{user_input}` tidak valid. Mohon masukkan angka saja."
        except Exception as e:
            response_text = f"❌ Terjadi kesalahan: `{e}`"
        
        keyboard = [[InlineKeyboardButton("Kembali ke menu Akses", callback_data=f"akses|menu|{selected_device}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_device: str):
    """Menambahkan user ID saat ini ke file akses."""
    user_id_to_add = update.effective_user.id
    
    try:
        with open(AKSES_FILE, 'r+') as f:
            lines = f.readlines()
            if str(user_id_to_add) in [line.strip() for line in lines]:
                response_text = f"✅ User ID `{user_id_to_add}` sudah ada."
            else:
                f.write(f"\n{user_id_to_add}")
                response_text = f"✅ User ID `{user_id_to_add}` berhasil ditambahkan."
        
        from bot import load_allowed_users
        load_allowed_users()
        
    except Exception as e:
        response_text = f"❌ Terjadi kesalahan saat menambah user: `{e}`"

    try: await update.callback_query.message.delete()
    except Exception: pass
        
    from bot import send_device_menu
    await send_device_menu(update, context, selected_device)
    
    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
        parse_mode='Markdown'
    )

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_to_del: str, selected_device: str):
    """Menghapus user ID dari file akses."""
    try:
        user_id = int(user_id_to_del)
        if user_id == update.effective_user.id:
            response_text = "❌ Anda tidak dapat menghapus diri sendiri."
        else:
            with open(AKSES_FILE, 'r') as infile, open(AKSES_EDIT_FILE, 'w') as outfile:
                removed = False
                for line in infile:
                    if line.strip() == str(user_id):
                        removed = True
                    else:
                        outfile.write(line)
            os.replace(AKSES_EDIT_FILE, AKSES_FILE)
            
            if removed:
                response_text = f"✅ User ID `{user_id}` berhasil dihapus."
            else:
                response_text = f"❌ User ID `{user_id}` tidak ditemukan."
            
            from bot import load_allowed_users
            load_allowed_users()

    except Exception as e:
        response_text = f"❌ Terjadi kesalahan saat menghapus user: `{e}`"

    try: await update.callback_query.message.delete()
    except Exception: pass
        
    from bot import send_device_menu
    await send_device_menu(update, context, selected_device)

    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
        parse_mode='Markdown'
    )
