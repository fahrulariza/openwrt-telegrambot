#!/bin/sh

# Hentikan bot sebelum memulai update
/www/assisten/bot/run_bot.sh stop

GITHUB_REPO="fahrulariza/openwrt-telegrambot"
REPO_URL="https://raw.githubusercontent.com/$GITHUB_REPO/master"
BOT_DIR="/www/assisten/bot"
TEMP_DIR="/tmp/bot_update"
VERSION_FILE="$BOT_DIR/VERSION"

# Cek argumen --force
FORCE_UPDATE=0
if [ "$1" = "--force" ]; then
    FORCE_UPDATE=1
    echo "Pembaruan paksa diaktifkan. Melewati pemeriksaan versi."
fi

# Dapatkan versi terbaru dari GitHub (hanya jika tidak ada pembaruan paksa)
if [ $FORCE_UPDATE -eq 0 ]; then
    echo "Memeriksa versi..."
    # Dapatkan versi lokal
    if [ -f "$VERSION_FILE" ]; then
        LOCAL_VERSION=$(cat "$VERSION_FILE")
    else
        LOCAL_VERSION="0.0"
    fi
    echo "Versi lokal: $LOCAL_VERSION"

    GITHUB_VERSION=$(wget -qO - "$REPO_URL/VERSION")
    if [ -z "$GITHUB_VERSION" ]; then
        echo "Gagal mendapatkan versi dari GitHub. Membatalkan pembaruan."
        /www/assisten/bot/run_bot.sh start
        exit 1
    fi
    echo "Versi GitHub: $GITHUB_VERSION"

    # Bandingkan versi
    if [ "$LOCAL_VERSION" = "$GITHUB_VERSION" ]; then
        echo "Bot sudah diperbarui ke versi terbaru. Tidak ada yang perlu diunduh."
        rm -rf "$TEMP_DIR"
        /www/assisten/bot/run_bot.sh start
        exit 0
    fi
    echo "Versi baru tersedia. Memulai proses pembaruan..."
fi

# --- SISA SKRIP UNTUK PROSES UNDUHAN DAN INSTALASI ---
echo "Mulai mengunduh file..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/cmd"

# ... (bagian unduhan file tidak berubah) ...

# Daftar file yang akan diunduh
FILES="bot.py VERSION run_bot.sh update.sh pre_run.sh restart.sh force_update.sh "
CMD_FILES="akses.py dhcp_leases.py force_update.py interface.py openclash.py reboot.py reload_bot.py status.py"

for file in $FILES; do
  wget -qO "$TEMP_DIR/$file" "$REPO_URL/$file"
  if [ $? -ne 0 ]; then
    echo "Gagal mengunduh $file. Menghentikan pembaruan."
    rm -rf "$TEMP_DIR"
    /www/assisten/bot/run_bot.sh start
    exit 1
  fi
done

for file in $CMD_FILES; do
  wget -qO "$TEMP_DIR/cmd/$file" "$REPO_URL/cmd/$file"
  if [ $? -ne 0 ]; then
    echo "Gagal mengunduh cmd/$file. Menghentikan pembaruan."
    rm -rf "$TEMP_DIR"
    /www/assisten/bot/run_bot.sh start
    exit 1
  fi
done

echo "Unduhan berhasil. Memasang file baru..."

cp -f "$TEMP_DIR/bot.py" "$BOT_DIR/bot.py"
cp -f "$TEMP_DIR/VERSION" "$BOT_DIR/VERSION"
cp -f "$TEMP_DIR/run_bot.sh" "$BOT_DIR/run_bot.sh"
cp -f "$TEMP_DIR/update.sh" "$BOT_DIR/update.sh"
cp -f "$TEMP_DIR/pre_run.sh" "$BOT_DIR/pre_run.sh"
cp -f "$TEMP_DIR/restart.sh" "$BOT_DIR/restart.sh"
cp -f "$TEMP_DIR/cmd/"* "$BOT_DIR/cmd/"

rm -rf "$TEMP_DIR"

echo "Memperbaiki izin dan format file..."
SCRIPTS="bot.py pre_run.sh restart.sh run_bot.sh update.sh"
for script in $SCRIPTS; do
  if [ -f "$BOT_DIR/$script" ]; then
    chmod +x "$BOT_DIR/$script"
    dos2unix "$BOT_DIR/$script"
  fi
done

echo "Pembaruan selesai. Memulai bot..."

# Jalankan ulang bot
/www/assisten/bot/run_bot.sh start

exit 0
