#!/bin/sh

# Ubah format file dari DOS ke UNIX
dos2unix /www/assisten/bot/run_bot.sh
dos2unix /www/assisten/bot/update.sh
dos2unix /www/assisten/bot/bot.py
dos2unix /www/assisten/bot/restart.sh

# Tambahkan izin eksekusi
chmod +x /www/assisten/bot/run_bot.sh
chmod +x /www/assisten/bot/update.sh
chmod +x /www/assisten/bot/bot.py
chmod +x /www/assisten/bot/restart.sh

echo "Persiapan file selesai."