import os
import sys
import importlib
import subprocess
import logging
import socket
import datetime
import asyncio
import random
import time
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from functools import wraps

# --- Konfigurasi Logging & Global State ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Konfigurasi Perangkat & Token ---
DEVICE_ID = socket.gethostname().strip()
os.environ['DEVICE_ID'] = DEVICE_ID
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
                    spec = importlib.util.spec_from_file_location(f"cmd.{module_name}", filepath)
                    if spec is None:
                        raise ImportError(f"Could not load module {module_name} from {filepath}")
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"cmd.{module_name}"] = module
                    spec.loader.exec_module(module)
                    
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
async def send_presence(context: ContextTypes.DEFAULT_TYPE):
    """Mengirim pesan 'ACTIVE' secara berkala ke chat dengan jeda acak."""
    global ACTIVE_DEVICES
    
    await asyncio.sleep(random.uniform(0, 5)) 

    for chat_id in context.application.bot_data.get('main_chat_ids', []):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"ACTIVE|{DEVICE_ID}",
                disable_notification=True,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Gagal mengirim pesan kehadiran ke chat {chat_id}: {e}")

async def clear_inactive_devices(context: ContextTypes.DEFAULT_TYPE):
    """Menghapus perangkat yang tidak mengirim sinyal kehadiran dalam 10 menit terakhir."""
    global ACTIVE_DEVICES
    now = datetime.datetime.now().timestamp()
    
    devices_to_check = list(context.application.bot_data.get('last_seen', {}).keys())
    inactive_devices = [
        device for device in devices_to_check
        if (now - context.application.bot_data['last_seen'].get(device, 0)) > 600
    ]
    for device in inactive_devices:
        ACTIVE_DEVICES.discard(device)
    
    logger.info(f"Perangkat tidak aktif dihapus: {inactive_devices}")

@check_access
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /start."""
    global ACTIVE_DEVICES
    chat_id = update.effective_chat.id
    
    if 'main_chat_ids' not in context.application.bot_data:
        context.application.bot_data['main_chat_ids'] = set()
    context.application.bot_data['main_chat_ids'].add(chat_id)
    
    ACTIVE_DEVICES.clear()
    ACTIVE_DEVICES.add(DEVICE_ID)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"ACTIVE|{DEVICE_ID}",
        disable_notification=True,
        disable_web_page_preview=True
    )
    
    await asyncio.sleep(3)
    
    await send_main_menu(update, context, sorted(list(ACTIVE_DEVICES)))

async def presence_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani pesan 'ACTIVE' dari perangkat lain."""
    global ACTIVE_DEVICES
    
    if update.effective_message.text and update.effective_message.text.startswith("ACTIVE|"):
        device_id = update.effective_message.text.split('|')[1]
        
        if 'last_seen' not in context.application.bot_data:
            context.application.bot_data['last_seen'] = {}
        context.application.bot_data['last_seen'][device_id] = datetime.datetime.now().timestamp()

        if device_id not in ACTIVE_DEVICES:
            ACTIVE_DEVICES.add(device_id)
            logger.info(f"Perangkat baru terdeteksi: {device_id}")

        try:
            await update.effective_message.delete()
        except Exception:
            pass

async def reload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani pesan RELOAD|ALL untuk memaksa pembaruan."""
    
    if update.effective_message.text == "RELOAD|ALL":
        try:
            await update.effective_message.delete()
        except Exception:
            pass
            
        logger.info(f"Sinyal RELOAD|ALL diterima di perangkat '{DEVICE_ID}'. Memulai pembaruan paksa.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔄 **{os.environ.get('DEVICE_ID')}** menerima sinyal pembaruan paksa. Memulai ulang bot...",
            parse_mode='Markdown'
        )
        
        # Jalankan skrip update.sh dengan argumen --force
        subprocess.Popen(['/bin/sh', os.path.join(SCRIPT_DIR, 'update.sh'), '--force'])
        await context.application.stop()
        
@check_access
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani semua tombol yang ditekan."""
    query = update.callback_query
    await query.answer()
    
    command_data = query.data.strip()
    command_parts = command_data.split('|')
    action = command_parts[0]
    
    try:
        await query.message.delete()
    except telegram.error.BadRequest as e:
        if "message to delete not found" in str(e):
            logger.warning("Gagal menghapus pesan, pesan sudah terhapus. Melanjutkan.")
        else:
            logger.error(f"Gagal menghapus pesan: {e}")
            
    if action == "back_to_main_menu":
        await send_main_menu(update, context, sorted(list(ACTIVE_DEVICES)))
        return
    
    if action == "select":
        selected_device = command_parts[1]
        await send_device_menu(update, context, selected_device)
        return
    
    if action == "install_update":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 Memulai proses instalasi pembaruan. Bot akan memulai ulang setelah selesai.")
        # Panggil update.sh tanpa argumen --force
        subprocess.Popen(['/bin/sh', os.path.join(SCRIPT_DIR, 'update.sh')])
        return
    
    if len(command_parts) >= 3 and action in LOADED_MODULES:
        command_name = action
        selected_device = command_parts[2]
        
        if selected_device == DEVICE_ID:
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

    remote_device_id = "UNKNOWN_DEVICE"
    if len(command_parts) >= 3:
        remote_device_id = command_parts[2]
    
    logger.warning(f"Tombol ditekan oleh '{remote_device_id}' untuk perintah '{action}', tetapi tidak cocok dengan DEVICE_ID lokal '{DEVICE_ID}'. Mengabaikan.")

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, devices_list) -> Message:
    """Mengirim menu utama pilihan perangkat dan mengembalikan objek pesan."""
    keyboard = [[InlineKeyboardButton(device, callback_data=f"select|{device}")] for device in sorted(devices_list)]
    
    update_script_path = os.path.join(SCRIPT_DIR, 'update.sh')
    if os.path.exists(update_script_path):
        keyboard.append([InlineKeyboardButton("Install Update", callback_data="install_update")])
        
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
    application.add_handler(CommandHandler("start", check_access(start)))
    application.add_handler(CallbackQueryHandler(check_access(button_handler)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^ACTIVE\|.*'), presence_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^RELOAD\|ALL'), reload_handler))
    
    application.job_queue.run_repeating(send_presence, interval=180, first=5)
    application.job_queue.run_repeating(clear_inactive_devices, interval=600, first=10)

    logger.info("Application started. Bot sedang aktif.")
    
    try:
        asyncio.run(application.run_polling(allowed_updates=Update.ALL_TYPES))
    except telegram.error.Conflict:
        logger.warning("Token sedang digunakan oleh bot lain. Menunggu 5 detik...")
        time.sleep(5)
        os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        logger.error(f"Kesalahan tak terduga: {e}. Bot akan keluar.")
        
if __name__ == '__main__':
    main()
