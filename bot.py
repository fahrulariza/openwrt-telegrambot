import logging
import os
import importlib
import asyncio
import datetime
import socket
import sys
import traceback
import atexit
import signal
from functools import wraps
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from asyncio import CancelledError

# Atur logging ke tingkat INFO
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Konfigurasi Perangkat ---
DEVICE_ID = socket.gethostname().strip()
logger.info(f"DEVICE_ID lokal yang terdeteksi: '{DEVICE_ID}'")

# --- Konfigurasi Lokasi File ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.txt")
AKSES_FILE = os.path.join(SCRIPT_DIR, "akses.txt")
CMD_FOLDER = os.path.join(SCRIPT_DIR, "cmd")
PID_FILE = "/tmp/run_bot.pid"

# --- Global State ---
LAST_COMMAND_MESSAGE_ID = {}
ALLOWED_USERS = set()
# Inisialisasi daftar perangkat aktif
ACTIVE_DEVICES = {DEVICE_ID}

# --- Fungsi Pembantu & Keamanan ---
def check_and_create_lock():
    """Memeriksa dan membuat lock file untuk memastikan hanya satu instance yang berjalan."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            # Cek apakah proses dengan PID ini masih berjalan
            os.kill(pid, 0)
            logger.error(f"Instance bot lain sudah berjalan dengan PID {pid}. Keluar.")
            sys.exit(1)
        except (ValueError, OSError):
            # File lock 'stale', hapus
            os.remove(PID_FILE)
    
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    # Daftarkan fungsi untuk menghapus lock file saat keluar
    atexit.register(lambda: os.remove(PID_FILE) if os.path.exists(PID_FILE) else None)

def get_token(filename=TOKEN_FILE):
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
        os.system(f"dos2unix {filepath}")
        os.chmod(filepath, os.stat(filepath).st_mode | 0o111)
        logger.info(f"Berhasil memproses (dos2unix, chmod +x) file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Gagal memproses file {filepath}: {e}")
        return False

# --- Fungsi Menu & Handler ---
@check_access
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mencoba menghapus pesan bot sebelumnya lalu mengirim menu utama."""
    chat_id = update.effective_chat.id
    
    try:
        await update.effective_message.delete()
    except Exception as e:
        logger.warning(f"Gagal menghapus pesan '/start': {e}")

    start_message_id = update.effective_message.message_id
    for message_id in range(start_message_id - 10, start_message_id):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
    
    # 1. Mengirim pesan awal untuk deteksi
    initial_message = await update.effective_message.reply_text("Mencari perangkat aktif...")
    
    # Simpan message_id untuk diedit
    context.chat_data['discovery_message_id'] = initial_message.message_id
    context.chat_data['active_devices'] = {DEVICE_ID}

    # Kirim sinyal kehadiran bot lokal
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"ACTIVE|{DEVICE_ID}",
        disable_notification=True,
        disable_web_page_preview=True
    )
    
    # 2. Tunggu 3 detik untuk mengumpulkan respons
    await asyncio.sleep(3)
    
    # 3. Hapus pesan sinyal kehadiran dan tampilkan menu final
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
        await send_main_menu(update, context, list(ACTIVE_DEVICES))


@check_access
async def presence_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani pesan 'ACTIVE' dari perangkat lain."""
    if 'discovery_message_id' in context.chat_data and update.effective_message.text and update.effective_message.text.startswith("ACTIVE|"):
        device_id = update.effective_message.text.split('|')[1]
        
        # Tambahkan perangkat baru ke daftar aktif
        if device_id not in context.chat_data['active_devices']:
            context.chat_data['active_devices'].add(device_id)
            logger.info(f"Perangkat baru terdeteksi: {device_id}")

            # Edit pesan deteksi untuk menampilkan perangkat yang diperbarui
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
    """Menangani tombol yang ditekan."""
    query = update.callback_query
    await query.answer()

    now = datetime.datetime.now(datetime.timezone.utc)
    message_time = query.message.date.astimezone(datetime.timezone.utc)
    time_diff = now - message_time

    if time_diff.total_seconds() > 180:
        logger.warning("Mencegah eksekusi perintah karena terlalu lama.")
        await query.message.reply_text("Perintah ini sudah kedaluwarsa (lebih dari 3 menit). Silakan ketik ulang /start.")
        return

    command_data = query.data.strip()
    command_parts = command_data.split('|')
    action = command_parts[0]
    
    if action == "back_to_main_menu":
        try: 
            await query.message.delete()
        except Exception: 
            pass
        await send_main_menu(update, context, list(ACTIVE_DEVICES))
        return
    
    if action == "back_to_device_menu":
        try:
            await query.message.delete()
        except Exception: 
            pass
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
    
    if action in [f.split('.')[0] for f in os.listdir(CMD_FOLDER)]:
        command_name = action
        selected_device = command_parts[2]

        if selected_device == DEVICE_ID:
            logger.info(f"Perintah '{command_name}' cocok dengan DEVICE_ID lokal. Menjalankan skrip...")
            
            try:
                chat_id = update.effective_chat.id
                
                if chat_id in LAST_COMMAND_MESSAGE_ID:
                    try:
                        await context.bot.delete_message(chat_id=chat_id, message_id=LAST_COMMAND_MESSAGE_ID[chat_id])
                    except Exception as e:
                        logger.warning(f"Gagal menghapus pesan lama: {e}")
                
                module = importlib.import_module(f"cmd.{command_name}")
                message = await module.execute(update, context, command_data=command_data)
                
                if message:
                    LAST_COMMAND_MESSAGE_ID[chat_id] = message.message_id
                
                logger.info(f"Perintah /{command_name} berhasil dijalankan.")
            except Exception as e:
                logger.error(f"Gagal menjalankan perintah /{command_name} pada {DEVICE_ID}: {e}")
                error_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Gagal menjalankan perintah `/{command_name}` pada `{DEVICE_ID}`. Terjadi kesalahan: `{e}`",
                    parse_mode='Markdown'
                )
                if error_message: 
                    LAST_COMMAND_MESSAGE_ID[chat_id] = error_message.message_id
                
                await send_device_menu(update, context, selected_device)
        else:
            logger.info(f"Tombol ditekan, tetapi tidak cocok dengan DEVICE_ID lokal ('{selected_device}' != '{DEVICE_ID}'). Mengabaikan.")

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
    commands_list = []
    for filename in os.listdir(CMD_FOLDER):
        if filename.endswith('.py') and filename != '__init__.py':
            command_name = filename.replace('.py', '')
            commands_list.append(command_name)
    
    commands_list.sort()
    
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
    chat_id = update.effective_chat.id
    LAST_COMMAND_MESSAGE_ID[chat_id] = message.message_id

def main() -> None:
    try:
        check_and_create_lock()
        token = get_token()
        if not token:
            logger.error("Token tidak ditemukan. Keluar.")
            sys.exit(1)
        
        load_allowed_users()

        application = Application.builder().token(token).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Tambahkan handler untuk mendeteksi pesan 'ACTIVE'
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^ACTIVE\|.*'), check_access(presence_handler)))

        from cmd.akses import handle_user_input
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_access(handle_user_input)))

        if not os.path.exists(CMD_FOLDER):
            os.makedirs(CMD_FOLDER)
        
        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(CMD_FOLDER, filename)
                process_new_file(filepath)
                
                command_name = filename.replace('.py', '')
                try:
                    module = importlib.import_module(f"cmd.{command_name}")
                    application.add_handler(CommandHandler(command_name, check_access(module.execute)))
                    logger.info(f"Perintah dimuat: /{command_name}")
                except Exception as e:
                    logger.error(f"Gagal memuat perintah /{command_name}: {e}")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

    except CancelledError:
        logger.info("Polling dibatalkan, bot akan berhenti.")
    except Exception as e:
        logger.error(f"Terjadi kesalahan fatal: {e}")
        logger.error(traceback.format_exc())
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
if __name__ == '__main__':
    main()