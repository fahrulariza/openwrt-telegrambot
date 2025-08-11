🌟 Asisten Bot Telegram untuk OpenWrt
<div align="center"> <img src="https://raw.githubusercontent.com/fahrulariza/openwrt-telegrambot/master/assets/logo.png" alt="Logo Bot Telegram OpenWrt" width="200"/> <h1>Asisten Bot Telegram OpenWrt</h1> <p>Cara pintar mengelola router OpenWrt melalui Telegram!</p>
https://img.shields.io/github/license/fahrulariza/openwrt-telegrambot
https://img.shields.io/badge/python-3.7%252B-blue
https://img.shields.io/badge/Telegram%2520Bot%2520API-v20.5%252B-brightgreen

</div>
✨ Fitur Unggulan
Fitur	Keterangan
🔧 Kontrol Penuh	Jalankan perintah shell, pantau status sistem, dan kelola layanan langsung dari Telegram
🎨 Antarmuka Interaktif	Tombol keyboard inline untuk navigasi mudah tanpa mengetik perintah manual
🔔 Notifikasi Real-time	Dapatkan pemberitahuan instan tentang status router Anda
🔒 Akses Aman	Sistem whitelist memastikan hanya pengguna terdaftar yang bisa mengontrol
📊 Pemantauan Sistem	Cek penggunaan CPU, memori, uptime, dan statistik jaringan dengan perintah sederhana
� Panduan Instalasi Cepat
📋 Persyaratan
Pastikan router OpenWrt Anda telah terinstal paket-paket berikut:

bash
opkg update
opkg install python3 python3-pip dos2unix wget git-http
⚡ Langkah Instalasi
Clone Repository

bash
cd /www/
git clone https://github.com/fahrulariza/openwrt-telegrambot.git assisten
Konfigurasi Bot & Akses

bash
# Set Token Bot Telegram Anda
echo "TOKEN_BOT_ANDA" > /www/assisten/bot/token.txt

# Tambahkan ID User Telegram (dapatkan dari @userinfobot)
echo "ID_USER_ANDA" > /www/assisten/bot/akses.txt
Instalasi Dependensi Python

bash
cd /www/assisten/bot
pip install -r requirements.txt
Atur Izin File

bash
chmod +x /www/assisten/bot/*.sh
chmod +x /www/assisten/bot/bot.py
dos2unix /www/assisten/bot/*.sh
Mulai Bot

bash
/www/assisten/bot/run_bot.sh start
🎮 Perintah Dasar
Perintah	Fungsi
/start	Memulai bot dan menampilkan menu utama
/status	Menampilkan ringkasan status sistem
/reboot	Me-restart router
/services	Kelola layanan yang sedang berjalan
/speedtest	Tes kecepatan internet
/help	Menampilkan informasi bantuan
💡 Tips Penggunaan
Jalankan di Background: Gunakan run_bot.sh start untuk menjaga bot tetap berjalan setelah sesi SSH berakhir

Pembaruan Otomatis: Bot bisa memeriksa pembaruan secara otomatis

Perintah Kustom: Anda bisa menambahkan perintah khusus di folder commands

🤝 Berkontribusi
Kami menerima kontribusi! Silakan ajukan issue atau pull request untuk membantu pengembangan proyek ini.

📜 Lisensi
Proyek ini menggunakan lisensi MIT - lihat file LICENSE untuk detailnya.

<div align="center"> <p>Nikmati kemudahan mengelola router OpenWrt melalui Telegram! ✨</p> <p>Kirim <code>/start</code> ke bot Anda untuk memulai!</p> </div>
