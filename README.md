<div align="center">
<img src="https://raw.githubusercontent.com/fahrulariza/openwrt-telegrambot/master/assets/logo.png" alt="OpenWrt Telegram Bot Logo" width="200"/>
<h1>Asisten Bot Telegram untuk OpenWrt</h1>
<p>Kelola router OpenWrt Anda dengan mudah melalui bot Telegram!</p>
</div>

## 🚀 Fitur Utama
- **Kontrol Penuh**: Jalankan perintah shell, pantau status sistem, dan kelola layanan langsung dari Telegram.
- **Antarmuka Interaktif**: Menggunakan Inline Keyboard untuk navigasi yang mudah tanpa mengetik perintah manual.
- **Notifikasi Instan**: Terima notifikasi real-time tentang status router Anda.
- **Keamanan Terjamin**: Akses hanya diberikan kepada User ID yang telah disetujui.

## 🛠️ Persiapan
Tool yang Dibutuhkan
Sebelum memulai, pastikan Anda telah menginstal tool berikut di OpenWrt Anda:

Bash

#### Perbarui daftar paket
- `opkg update`

## Pasang paket yang diperlukan
- `opkg install python3 python3-pip dos2unix wget git-http`

Keterangan Tool
python3: Bahasa pemrograman utama untuk menjalankan bot.

python3-pip: Manajer paket untuk menginstal pustaka Python yang dibutuhkan.

dos2unix: Untuk mengonversi format file skrip.

wget: Untuk mengunduh file dari internet.

git-http: Digunakan untuk proses instalasi yang lebih mudah.

### ⚙️ Panduan Instalasi
Ikuti langkah-langkah di bawah ini untuk menginstal bot di router OpenWrt Anda.
<p>
Langkah 1: Kloning Repositori
Masuk ke router OpenWrt Anda melalui SSH, lalu jalankan perintah ini untuk mengunduh kode bot:

Bash

cd /www/
git clone https://github.com/fahrulariza/openwrt-telegrambot.git assisten
Langkah 2: Konfigurasi Token Bot & Akses Pengguna
Buat bot Telegram baru melalui @BotFather dan dapatkan token API-nya.

Buat file token.txt di folder assisten/bot/ dan masukkan token Anda di dalamnya.

Bash

echo "TOKEN_BOT_ANDA" > /www/assisten/bot/token.txt
Dapatkan ID pengguna Telegram Anda dari @userinfobot.

Buat file akses.txt di folder yang sama dan masukkan ID pengguna Anda.

Bash

echo "ID_PENGGUNA_ANDA" > /www/assisten/bot/akses.txt
Langkah 3: Instal Pustaka Python
Masuk ke direktori bot dan instal semua pustaka yang diperlukan.

Bash

cd /www/assisten/bot
pip install -r requirements.txt
Langkah 4: Jalankan Skrip Persiapan
Skrip ini akan memastikan semua file memiliki izin eksekusi yang benar.

Bash

chmod +x /www/assisten/bot/run_bot.sh
chmod +x /www/assisten/bot/update.sh
chmod +x /www/assisten/bot/bot.py
dos2unix /www/assisten/bot/*.sh
Langkah 5: Jalankan Bot
Gunakan skrip run_bot.sh untuk memulai bot. Bot akan berjalan di latar belakang.

Bash

/www/assisten/bot/run_bot.sh start
</p>
<div align="center">
<p>Selesai! Sekarang bot Anda siap digunakan. Buka Telegram dan kirim perintah <code>/start</code> ke bot Anda.</p>
</div>
