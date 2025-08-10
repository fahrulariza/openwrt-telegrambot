#!/bin/sh

case "$1" in
  start)
    echo "Menghentikan bot lama..."
    killall python3 2>/dev/null
    sleep 2
    echo "Menjalankan bot baru..."
    /usr/bin/python3 /www/assisten/bot/bot.py &
    ;;
  stop)
    echo "Menghentikan bot..."
    killall python3 2>/dev/null
    ;;
  *)
    echo "Penggunaan: $0 {start|stop}"
    exit 1
    ;;
esac

exit 0
