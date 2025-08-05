#!/bin/sh

echo "Memulai proses restart bot..."

# Cari ID proses (PID) dari bot.py dan hentikan
ps | grep -v 'grep' | grep -q 'python3 /www/assisten/bot/bot.py'
if [ $? -eq 0 ]; then
  PID=$(ps | grep 'python3 /www/assisten/bot/bot.py' | grep -v 'grep' | awk '{print $1}')
  kill -9 $PID
  echo "Proses bot.py (PID: $PID) berhasil dihentikan."
else
  echo "Proses bot.py tidak ditemukan. Melanjutkan..."
fi

echo "run_bot.sh akan memulai ulang bot secara otomatis."

exit 0