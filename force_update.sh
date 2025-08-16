#!/bin/sh

# File ini berfungsi untuk secara paksa memulai proses pembaruan.
# Skrip ini bisa dipanggil oleh bot atau secara manual.

# Tentukan lokasi skrip
SCRIPT_DIR="/www/assisten/bot"

# Cek apakah skrip update.sh ada
if [ ! -f "$SCRIPT_DIR/update.sh" ]; then
    echo "Kesalahan: Skrip update.sh tidak ditemukan!"
    exit 1
fi

# Jalankan skrip update.sh dengan argumen paksa
# Argumen --force akan memaksa pembaruan tanpa memeriksa versi
/bin/sh "$SCRIPT_DIR/update.sh" --force

exit 0
