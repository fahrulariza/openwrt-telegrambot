#!/bin/sh

# File ini berfungsi untuk mengelola pembaruan bot,
# baik secara normal maupun paksa.

# Tentukan lokasi dan URL repositori
SCRIPT_DIR="/www/assisten/bot"
GITHUB_REPO="fahrulariza/openwrt-telegrambot"
REPO_URL="https://raw.githubusercontent.com/$GITHUB_REPO/master"
VERSION_FILE="$SCRIPT_DIR/VERSION"
TEMP_DIR="/tmp/bot_update"

# --- Tangani Argumen ---
FORCE_UPDATE=0
CHECK_ONLY=0

if [ "$1" = "--force" ]; then
    FORCE_UPDATE=1
    echo "Pembaruan paksa diaktifkan."
elif [ "$1" = "--check" ]; then
    CHECK_ONLY=1
fi

# --- Cek Versi ---
echo "Memeriksa versi..."
if [ -f "$VERSION_FILE" ]; then
    LOCAL_VERSION=$(cat "$VERSION_FILE")
else
    LOCAL_VERSION="0.0"
fi
echo "Versi lokal: $LOCAL_VERSION"

GITHUB_VERSION=$(wget -qO - "$REPO_URL/VERSION")
if [ -z "$GITHUB_VERSION" ]; then
    echo "Gagal mendapatkan versi dari GitHub."
    if [ $CHECK_ONLY -eq 1 ]; then
        exit 1
    fi
    /www/assisten/bot/run_bot.sh start
    exit 1
fi
echo "Versi GitHub: $GITHUB_VERSION"

# Jika hanya mode cek, keluar setelah menampilkan versi
if [ $CHECK_ONLY -eq 1 ]; then
    exit 0
fi

# --- Bandingkan Versi (Jika Bukan Pembaruan Paksa) ---
if [ $FORCE_UPDATE -eq 0 ] && [ "$LOCAL_VERSION" = "$GITHUB_VERSION" ]; then
    echo "Bot sudah diperbarui ke versi terbaru. Tidak ada yang perlu diunduh."
    /www/assisten/bot/run_bot.sh start
    exit 0
fi

# --- Proses Pembaruan ---
echo "Mulai mengunduh file..."

# Hentikan bot sebelum memulai unduhan
/www/assisten/bot/run_bot.sh stop
sleep 2

# Hapus dan buat direktori sementara
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/cmd"

# Daftar file yang akan diunduh
FILES="bot.py VERSION run_bot.sh update.sh pre_run.sh restart.sh force_update.sh"
CMD_FILES="akses.py dhcp_leases.py force_update.py help.py interface.py openclash.py reboot.py reload_bot.py status.py update.py terminal.py cekmodule.py wan.py"

# Unduh file utama
for file in $FILES; do
  wget -qO "$TEMP_DIR/$file" "$REPO_URL/$file"
  if [ $? -ne 0 ]; then
    echo "Gagal mengunduh $file. Menghentikan pembaruan."
    rm -rf "$TEMP_DIR"
    /www/assisten/bot/run_bot.sh start
    exit 1
  fi
done

# Unduh file perintah
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

# Salin file ke direktori bot
cp -f "$TEMP_DIR/bot.py" "$SCRIPT_DIR/bot.py"
cp -f "$TEMP_DIR/VERSION" "$SCRIPT_DIR/VERSION"
cp -f "$TEMP_DIR/run_bot.sh" "$SCRIPT_DIR/run_bot.sh"
cp -f "$TEMP_DIR/update.sh" "$SCRIPT_DIR/update.sh"
cp -f "$TEMP_DIR/pre_run.sh" "$SCRIPT_DIR/pre_run.sh"
cp -f "$TEMP_DIR/restart.sh" "$SCRIPT_DIR/restart.sh"
cp -f "$TEMP_DIR/force_update.sh" "$SCRIPT_DIR/force_update.sh"
cp -f "$TEMP_DIR/cmd/"* "$SCRIPT_DIR/cmd/"

rm -rf "$TEMP_DIR"

echo "Memperbaiki izin dan format file..."
# Konversi ke format Unix dan berikan izin eksekusi
SCRIPTS="bot.py pre_run.sh restart.sh run_bot.sh update.sh force_update.sh"
for script in $SCRIPTS; do
  if [ -f "$SCRIPT_DIR/$script" ]; then
    dos2unix "$SCRIPT_DIR/$script"
    chmod +x "$SCRIPT_DIR/$script"
  fi
done

echo "Pembaruan selesai. Memulai bot..."

# Jalankan ulang bot
/www/assisten/bot/run_bot.sh start

exit 0
