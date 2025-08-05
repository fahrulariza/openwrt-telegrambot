import os
import datetime
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
    """Mengambil dan menampilkan daftar DHCP leases dari file /tmp/dhcp.leases."""
    
    selected_device = 'local'
    if 'command_data' in kwargs:
        command_parts = kwargs['command_data'].split('|')
        if len(command_parts) > 2:
            selected_device = command_parts[2]

    leases_file = '/tmp/dhcp.leases'

    if not os.path.exists(leases_file):
        await update.effective_message.reply_text("❌ File dhcp.leases tidak ditemukan. Mungkin tidak ada perangkat yang terhubung.")
        return

    try:
        with open(leases_file, 'r') as f:
            lines = f.readlines()

        if not lines:
            await update.effective_message.reply_text("Tidak ada DHCP leases aktif yang ditemukan.")
            return

        response_text = "✨ **Daftar Perangkat Terhubung (DHCP Leases)** ✨\n\n"
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    expiry_timestamp = int(parts[0])
                    mac_address = parts[1]
                    ip_address = parts[2]
                    hostname = parts[3]

                    now_timestamp = int(datetime.datetime.now().timestamp())
                    leasetime_remaining = expiry_timestamp - now_timestamp
                    
                    if leasetime_remaining > 0:
                        lease_timedelta = datetime.timedelta(seconds=leasetime_remaining)
                        hours, remainder = divmod(lease_timedelta.total_seconds(), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        lease_str = f"{int(hours)}j {int(minutes)}m {int(seconds)}d"
                    else:
                        lease_str = "Kedaluwarsa"

                    response_text += f"**Hostname:** `{hostname}`\n"
                    response_text += f"**IP Address:** `{ip_address}`\n"
                    response_text += f"**MAC Address:** `{mac_address}`\n"
                    response_text += f"**Sisa Waktu Lease:** `{lease_str}`\n"
                    response_text += "––––––––––––––––––––\n"

                except (ValueError, IndexError) as e:
                    logger.warning(f"Melewatkan baris tidak valid di dhcp.leases: {line.strip()}. Error: {e}")
                    continue

        keyboard = [[InlineKeyboardButton("Kembali ke menu pilih perintah", callback_data=f"back_to_device_menu|{selected_device}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Terjadi kesalahan saat membaca file dhcp.leases: {e}")
        await update.effective_message.reply_text(f"❌ Terjadi kesalahan tak terduga: `{e}`", parse_mode='Markdown')