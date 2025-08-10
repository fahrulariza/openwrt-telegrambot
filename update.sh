#!/bin/sh

# Hentikan bot sebelum memulai update
/www/assisten/bot/run_bot.sh stop

GITHUB_REPO="fahrulariza/openwrt-telegrambot"
REPO_URL="https://raw.githubusercontent.com/$GITHUB_REPO/master"
BOT_DIR="/www/assisten/bot"
TEMP_DIR="/tmp/bot_update"

echo "Mulai mengunduh file..."

# Buat direktori sementara dan pastikan bersih
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/cmd"

# Daftar file yang akan diunduh
FILES="bot.py VERSION run_bot.sh update.sh"
CMD_FILES="akses.py dhcp_leases.py interface.py openclash.py reboot.py reload_bot.py status.py"

# Unduh file utama
for file in $FILES; do
  wget -qO "$TEMP_DIR/$file" "$REPO_URL/$file"
  if [ $? -ne 0 ]; then
    echo "Gagal mengunduh $file. Menghentikan pembaruan."
    exit 1
  fi
done

# Unduh file di folder cmd
for file in $CMD_FILES; do
  wget -qO "$TEMP_DIR/cmd/$file" "$REPO_URL/cmd/$file"
  if [ $? -ne 0 ]; then
    echo "Gagal mengunduh cmd/$file. Menghentikan pembaruan."
    exit 1
  fi
done

echo "Unduhan berhasil. Memasang file baru..."

# Salin file baru ke direktori bot
cp -f "$TEMP_DIR/bot.py" "$BOT_DIR/bot.py"
cp -f "$TEMP_DIR/VERSION" "$BOT_DIR/VERSION"
cp -f "$TEMP_DIR/run_bot.sh" "$BOT_DIR/run_bot.sh"
cp -f "$TEMP_DIR/update.sh" "$BOT_DIR/update.sh"
cp -f "$TEMP_DIR/cmd/"* "$BOT_DIR/cmd/"

# Hapus direktori sementara
rm -rf "$TEMP_DIR"

# Perbaiki format dan izin eksekusi
echo "Memperbaiki izin file..."
chmod +x "$BOT_DIR/bot.py"
chmod +x "$BOT_DIR/pre_run.sh"
chmod +x "$BOT_DIR/restart.sh"
chmod +x "$BOT_DIR/run_bot.sh"
chmod +x "$BOT_DIR/update.sh"
dos2unix "$BOT_DIR/bot.py"
dos2unix "$BOT_DIR/pre_run.sh"
dos2unix "$BOT_DIR/restart.sh"
dos2unix "$BOT_DIR/run_bot.sh"
dos2unix "$BOT_DIR/update.sh"

echo "Pembaruan selesai. Memulai bot..."

# Jalankan ulang bot
/www/assisten/bot/run_bot.sh start

exit 0