#!/bin/sh

# Jalankan bot.py dalam loop untuk memastikan bot selalu berjalan
while true; do
  echo "Menjalankan bot... $(date)"
  python3 /www/assisten/bot/bot.py
  echo "Bot berhenti. Akan dimulai ulang dalam 5 detik... $(date)"
  sleep 5
done