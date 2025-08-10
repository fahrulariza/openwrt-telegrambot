import os
import importlib
import subprocess
import logging
import socket
import datetime
import asyncio
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from functools import wraps

# --- Konfigurasi Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Konfigurasi Perangkat & Token ---
DEVICE_ID = socket.gethostname().strip()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.txt")
AKSES_FILE = os.path.join(SCRIPT_DIR, "akses.txt")
CMD_FOLDER = os.path.join(SCRIPT_DIR, "cmd")
PID_FILE = "/tmp/run_bot.pid"

# --- Global State ---
ALLOWED_USERS = set()
LOADED_MODULES = {}
LAST_COMMAND_MESSAGE_ID = {}
ACTIVE_DEVICES = {DEVICE_ID}

def get_token(filename=TOKEN_FILE):
    """Membaca token bot dari file."""
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"File {filename} tidak ditemukan.")
        return None

def load_allowed_users(filename=AKSES_FILE):
    """Membaca user ID yang diizinkan dari file."""
    global ALLOWED_USERS
    new_users = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        new_users.add(int(line))
                    except ValueError:
                        logger.warning(f"ID pengguna tidak valid di {filename}: {line}")
    if new_users != ALLOWED_USERS:
        ALLOWED_USERS = new_users
        logger.info(f"Daftar user ID yang diizinkan diperbarui: {ALLOWED_USERS}")

def check_access(func):
    """Decorator untuk memeriksa apakah pengguna memiliki akses."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        load_allowed_users()
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            logger.warning(f"Akses ditolak untuk user ID: {user_id}")
            await update.effective_message.reply_text(
                "❌ Maaf, Anda tidak memiliki izin untuk mengakses bot ini."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def process_new_file(filepath):
    """Mengonversi file ke format Unix dan menambahkan izin eksekusi."""
    try:
        subprocess.run(['dos2unix', filepath], check=True, capture_output=True)
        os.chmod(filepath, os.stat(filepath).st_mode | 0o111)
        logger.info(f"Berhasil memproses (dos2unix, chmod +x) file: {filepath}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Gagal memproses file {filepath}: {e.stderr.decode().strip()}")
    except Exception as e:
        logger.error(f"Gagal memproses file {filepath}: {e}")
    return False

def load_commands(application: Application):
    """Memuat semua skrip Python dari direktori 'cmd'."""
    if not os.path.isdir(CMD_FOLDER):
        logger.error(f"Direktori '{CMD_FOLDER}' tidak ditemukan.")
        return
    
    for filename in os.listdir(CMD_FOLDER):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            filepath = os.path.join(CMD_FOLDER, filename)
            
            if process_new_file(filepath):
                try:
                    module = importlib.import_module(f'cmd.{module_name}')
                    
                    LOADED_MODULES[module_name] = module
                    
                    if hasattr(module, 'execute'):
                        application.add_handler(CommandHandler(module_name, check_access(module.execute)))
                        logger.info(f"Perintah dimuat: /{module_name}")
                    else:
                        logger.info(f"Modul '{module_name}' dimuat, tetapi tidak memiliki CommandHandler.")
                except ImportError as e:
                    logger.error(f"Gagal memuat modul '{module_name}': {e}")
                except Exception as e:
                    logger.error(f"Kesalahan tak terduga saat memuat modul '{module_name}': {e}")

# --- Fungsi Menu & Handler ---
@check_access
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /start dan menampilkan menu utama."""
    chat_id = update.effective_chat.id
    try:
        await update.effective_message.delete()
    except Exception:
        pass
    
    # Tambahkan sedikit jeda acak untuk mencegah tabrakan
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    # Kirim pesan awal untuk deteksi hanya jika belum ada yang memulai
    if 'discovery_message_id' not in context.chat_data:
        initial_message = await update.effective_message.reply_text("Mencari perangkat aktif...")
        context.chat_data['discovery_message_id'] = initial_message.message_id
        context.chat_data['active_devices'] = {DEVICE_ID}

        # Kirim sinyal kehadiran bot lokal
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"ACTIVE|{DEVICE_ID}",
            disable_notification=True,
            disable_web_page_preview=True
        )
    
    await asyncio.sleep(3)
    
    # Hanya bot yang "menang" (memiliki discovery_message_id) yang akan mengirim menu
    if 'discovery_message_id' in context.chat_data:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=context.chat_data['discovery_message_id'])
        except Exception:
            pass
        finally:
            del context.chat_data['discovery_message_id']
            if 'active_devices' in context.chat_data:
                await send_main_menu(update, context, list(context.chat_data['active_devices']))
                del context.chat_data['active_devices']
    else:
        # Jika bot ini "kalah" (tidak memiliki discovery_message_id), ia tidak melakukan apa-apa.
        pass

@check_access
async def presence_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani pesan 'ACTIVE' dari perangkat lain."""
    if 'discovery_message_id' in context.chat_data and update.effective_message.text and update.effective_message.text.startswith("ACTIVE|"):
        device_id = update.effective_message.text.split('|')[1]
        if device_id not in context.chat_data['active_devices']:
            context.chat_data['active_devices'].add(device_id)
            logger.info(f"Perangkat baru terdeteksi: {device_id}")
            devices_list_str = "\n".join(sorted(list(context.chat_data['active_devices'])))
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=context.chat_data['discovery_message_id'],
                    text=f"Mencari perangkat aktif...\n\nPerangkat ditemukan:\n{devices_list_str}"
                )
            except Exception:
                pass
        try:
            await update.effective_message.delete()
        except Exception:
            pass

@check_access
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani semua tombol yang ditekan."""
    query = update.callback_query
    await query.answer()
    
    command_data = query.data.strip()
    command_parts = command_data.split('|')
    action = command_parts[0]
    
    if action in ["back_to_main_menu", "back_to_device_menu"]:
        try:
            await query.message.delete()
        except Exception:
            pass
        if action == "back_to_main_menu":
            await send_main_menu(update, context, list(ACTIVE_DEVICES))
        elif action == "back_to_device_menu":
            selected_device = command_parts[1]
            await send_device_menu(update, context, selected_device)
        return
    
    if action == "select":
        try:
            await query.message.delete()
        except Exception:
            pass
        selected_device = command_parts[1]
        await send_device_menu(update, context, selected_device)
        return
        
    if action in LOADED_MODULES:
        command_name = action
        selected_device = command_parts[2]
        
        if selected_device == DEVICE_ID:
            try:
                await query.message.delete()
            except Exception:
                pass
            
            try:
                await LOADED_MODULES[command_name].execute(update, context, command_data)
                logger.info(f"Perintah /{command_name} berhasil dijalankan pada '{DEVICE_ID}'.")
            except Exception as e:
                logger.error(f"Gagal menjalankan perintah /{command_name}: {e}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Terjadi kesalahan saat menjalankan perintah {command_name}."
                )
            return

    logger.warning(f"Tombol ditekan, tetapi tidak cocok dengan DEVICE_ID lokal ('{command_parts[2]}' != '{DEVICE_ID}'). Mengabaikan.")

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, devices_list) -> Message:
    """Mengirim menu utama pilihan perangkat dan mengembalikan objek pesan."""
    keyboard = [[InlineKeyboardButton(device, callback_data=f"select|{device}")] for device in sorted(devices_list)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        message = await update.callback_query.message.reply_text(
            "Halo! Silakan pilih perangkat yang ingin Anda kelola:",
            reply_markup=reply_markup
        )
    else:
        message = await update.effective_message.reply_text(
            "Halo! Silakan pilih perangkat yang ingin Anda kelola:",
            reply_markup=reply_markup
        )
    logger.info("Menu pemilihan perangkat berhasil dikirim.")
    return message

async def send_device_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_device: str) -> None:
    """Mengirim menu perintah untuk perangkat tertentu secara dinamis."""
    commands_list = sorted(list(LOADED_MODULES.keys()))
    
    keyboard = []
    for cmd in commands_list:
        keyboard.append([InlineKeyboardButton(cmd.capitalize(), callback_data=f"{cmd}|menu|{selected_device}")])
        
    keyboard.append([InlineKeyboardButton("Kembali ke Menu Utama", callback_data="back_to_main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Anda memilih `{selected_device}`. Silakan pilih perintah:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    logger.info(f"Menu perintah untuk '{selected_device}' berhasil dikirim.")

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    token = get_token()
    if not token:
        logger.error("Token tidak ditemukan. Keluar.")
        return

    logger.info(f"DEVICE_ID lokal yang terdeteksi: '{DEVICE_ID}'")
    load_allowed_users()

    application = Application.builder().token(token).build()
    
    load_commands(application)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^ACTIVE\|.*'), presence_handler))

    logger.info("Application started. Bot sedang aktif.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
