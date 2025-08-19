import logging
from telegram import Update
from telegram.ext import ContextTypes
import sys

# Versi Modul
VERSION = "1.1.0"

IS_MENU_COMMAND = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# --- Konten Bantuan ---
# Isi dari file perintah-module.md sudah diubah ke format HTML
HELP_TEXT = """
<b>Asisten Bot Telegram sederhana untuk OpenWrt</b>

Kelola router OpenWrt Anda dengan mudah melalui bot Telegram!

<b>Penjelasan setiap fungsi module</b>

<b>terminal.py</b>
modul untuk mengeksekusi perintah terminal dan menampilkan hasilnya di chat telegram bot
<code>/terminal</code> di Telegram, seperti:
<pre>
/terminal ps | grep bot
</pre>
maka hasil yang dikirim berupa
<pre>
31006 root      52676 S    /usr/bin/python3 /www/assisten/bot/bot.py
31155 root        1320 S    /bin/sh -c ps | grep bot
31158 root        1316 S    grep bot
</pre>

<b>cekmodule.py</b>
modul untuk mengeksekusi perintah terminal dan menampilkan hasilnya di chat telegram bot
<code>/cekmodule</code> di Telegram, seperti:
<pre>
/cekmodule
</pre>
maka hasil yang dikirim berupa
<pre>
📜 Daftar Modul yang Dimuat:

• Akses (v3.5.0) - <code>MENU</code>
• Cekmodule (v1.5.1) - <code>MENU</code>
• Dhcp_leases (v3.5.0) - <code>MENU</code>
• Force_update (v3.5.0) - <code>CMD</code>
• help (v1.1.0) - <code>CMD</code>
• Interface (v3.5.0) - <code>MENU</code>
• Openclash (v3.5.0) - <code>MENU</code>
• Proxy_openclash (v3.5.4) - <code>MENU</code>
• Reboot (v3.5.0) - <code>MENU</code>
• Reload_bot (v3.5.0) - <code>MENU</code>
• Status (v3.5.0) - <code>MENU</code>
• Terminal (v3.5.0) - <code>CMD</code>
• Update (v3.5.0) - <code>MENU</code>
• Wan (v1.0.2) - <code>MENU</code>
</pre>

<b>force_update.py</b>
modul untuk mengeksekusi perintah terminal memaksa update apapun versinya. berguna untuk memperbaiki script yang rusak atau error dengan memasang script yang terbaru

<code>/force_update</code> di Telegram, seperti:
<pre>
/force_update
</pre>
maka hasil yang dikirim berupa
<pre>
🚨 Memaksa pembaruan perangkat saat ini...
</pre>
"""

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                HELP_TEXT,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                HELP_TEXT,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Gagal mengirim pesan bantuan: {e}")
        error_message = f"❌ Terjadi kesalahan saat menampilkan bantuan."
        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)
