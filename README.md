<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/9/92/Openwrt_Logo.svg" alt="OpenWrt Telegram Bot Logo" width="200"/>

![License](https://img.shields.io/github/license/fahrulariza/openwrt-telegrambot)
[![GitHub All Releases](https://img.shields.io/github/downloads/fahrulariza/openwrt-telegrambot/total)]()
![Total Commits](https://img.shields.io/github/commit-activity/t/fahrulariza/openwrt-telegrambot)
![Top Language](https://img.shields.io/github/languages/top/fahrulariza/openwrt-telegrambot)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/fahrulariza/openwrt-telegrambot/ci.yml)
![Open Issues](https://img.shields.io/github/issues/fahrulariza/openwrt-telegrambot)


<h1>Asisten Bot Telegram sederhana untuk OpenWrt</h1>
<p>Kelola router OpenWrt Anda dengan mudah melalui bot Telegram!</p>
</div>

## 🚀 Fitur Utama
- **Kontrol Penuh**: Jalankan perintah shell, pantau status sistem, dan kelola layanan langsung dari Telegram.
- **Antarmuka Interaktif**: Menggunakan Inline Keyboard untuk navigasi yang mudah tanpa mengetik perintah manual.
- **Notifikasi Instan**: Terima notifikasi real-time tentang status router Anda.
- **Keamanan Terjamin**: Akses hanya diberikan kepada User ID yang telah disetujui.
- **Module**: menambahkan dan menghapus module tanpa mengubah script utama hanya di folder `cmd`



### ⚙️ Struktur file Instalasi
```
/www/assisten/
        ├── bot/
        │   ├── cmd/       <<<<<<<<<<< folder utama berisi module perintah
        │   │   ├── __init__.py
        │   │   ├── akses.py
        │   │   ├── dhcp_leases.py
        │   │   ├── interface.py
        │   │   ├── openclash.py
        │   │   ├── reboot.py
        │   │   ├── reload_bot.py
        │   │   ├── status.py
        │   │   └── update.py
        │   ├── bot.py <<<<<<<<<<<<<<< script utama untuk menerima dan menjalankan perintah. 
        │   ├── README.md
        │   ├── restart.sh
        │   ├── run_bot.sh  <<<<<<<<<< script eksekusi untuk menjalankan bot.py
        │   ├── akses.txt <<<<<<<<<<<< berisi ID yang akan bisa mengakses perintah bot
        │   └── token.txt <<<<<<<<<<<< berisi token bot yang akan digunakan
        └── .git/
```
## 🛠️ Penjelasan Struktur File
> - **/www/assisten/bot**: Ini adalah direktori utama tempat semua kode bot berada.
> - folder **bot/**:
> 1. **cmd/**: Folder ini berisi semua modul perintah yang dapat dijalankan bot. Setiap file .py di sini (akses.py, status.py, dll.) adalah perintah terpisah yang akan dimuat secara dinamis oleh bot.py. File __init__.py kosong diperlukan agar Python mengenali cmd sebagai sebuah paket.
> 2. **bot.py**: Skrip utama bot yang menjalankan semua logika, menangani koneksi Telegram, memuat perintah, dan mengelola interaksi.
> 3. **README.md**: Berisi panduan instalasi dan deskripsi proyek.
> 4. **restart.sh**: Skrip shell untuk menghentikan dan memulai ulang bot.
> 5. **run_bot.sh**: Skrip utama untuk mengelola siklus hidup bot (mulai, berhenti, restart).
> 6. **akses.txt**: File teks berisi daftar User ID Telegram yang diizinkan untuk menggunakan bot.
> 7. **token.txt**: File teks berisi token API bot Anda dari BotFather.
> 8. **.git/**: Direktori ini dibuat oleh Git untuk mengelola riwayat versi proyek.

Struktur ini rapi, modular, dan memudahkan Anda untuk menambah, menghapus, atau mengelola perintah baru tanpa mengubah skrip utama `bot.py` hanya uploda module ke folder `cmd`.

## 🛠️ Persiapan
Tool yang Dibutuhkan
Sebelum memulai, pastikan telah menginstal tool berikut di OpenWrt :

melalui terminal di openwrt ikuti langkah dibawah ini

#### Perbarui daftar paket
```
opkg update
```
#### Pasang paket yang diperlukan
```
opkg install python3 python3-pip dos2unix wget git-http
```

> Keterangan Tool
> 1. **python3:** Bahasa pemrograman utama untuk menjalankan bot.
> 2. **python3-pip:** Manajer paket untuk menginstal pustaka Python yang dibutuhkan.
> 3. **dos2unix:** Untuk mengonversi format file skrip.
> 4. **wget:** Untuk mengunduh file dari internet.
> 5. **git-http:** Digunakan untuk proses instalasi yang lebih mudah.

#### Pasang library python yang diperlukan
```
pip install psutil
```
```
pip3 install python-telegram-bot
```
```
pip3 install paramiko
```
```
pip install "python-telegram-bot[job-queue]"
```

## ⚙️ Panduan Instalasi
Ikuti langkah-langkah di bawah ini untuk menginstal bot di router OpenWrt.
### Langkah 1: Kloning Repositori
Masuk ke router OpenWrt melalui `SSH` atau `Terminal LuCi`, lalu jalankan perintah ini untuk mengunduh kode bot dan menyimpannya ke folder assisten di `/www/assisten/bot`:

```
mkdir /www/assisten
mkdir /www/assisten/bot
cd /www/assisten/
git clone https://github.com/fahrulariza/openwrt-telegrambot.git bot
```
atau
1. Download manual [disini](https://github.com/fahrulariza/openwrt-telegrambot/archive/refs/heads/master.zip)
2. Letakkan semua file ke dalam folder `/www/asissten/bot/` sturktur bisa dilihat diatas. lanjut ke Lankah 2

### Langkah 2: Konfigurasi Token Bot & Akses Pengguna
Buat bot Telegram baru melalui @BotFather dan dapatkan token API-nya.

Buat file token.txt di folder assisten/bot/ dan masukkan token Anda di dalamnya.

```
echo "TOKEN_BOT_ANDA" > /www/assisten/bot/token.txt
```
Dapatkan ID pengguna Telegram Anda dari @userinfobot.

Buat file akses.txt di folder yang sama dan masukkan ID pengguna Anda.

```
echo "ID_PENGGUNA_ANDA" > /www/assisten/bot/akses.txt
```
### Langkah 3: Instal Pustaka Python
Masuk ke direktori bot dan instal semua pustaka yang diperlukan.

```
cd /www/assisten/bot
pip install -r requirements.txt
```
### Langkah 4: Jalankan Skrip Persiapan
Skrip ini akan memastikan semua file memiliki izin eksekusi yang benar.
```
chmod +x /www/assisten/bot/force_update.sh
chmod +x /www/assisten/bot/pre_run.sh
chmod +x /www/assisten/bot/restart.sh
chmod +x /www/assisten/bot/run_bot.sh
chmod +x /www/assisten/bot/update.sh
dos2unix /www/assisten/bot/force_update.sh
dos2unix /www/assisten/bot/pre_run.sh
dos2unix /www/assisten/bot/restart.sh
dos2unix /www/assisten/bot/run_bot.sh
dos2unix /www/assisten/bot/update.sh
dos2unix /www/assisten/bot/bot.py
chmod +x /www/assisten/bot/bot.py
dos2unix /www/assisten/bot/*.sh
```
Untuk memastikan semua file di folder cmd/ memiliki format dan izin yang benar, jalankan lagi perintah ini
```
cd /www/assisten/bot/cmd
dos2unix *.py
chmod +x *.py
```
### Langkah 5: Jalankan Bot Manual
Gunakan skrip run_bot.sh untuk memulai bot. Bot akan berjalan di latar belakang.
```
/www/assisten/bot/run_bot.sh start
```

Cara Alternatif (Init Script)
Metode yang lebih rapi dan direkomendasikan di OpenWrt adalah membuat `init.d` script khusus untuk bot Anda. Ini memberikan kontrol yang lebih baik (misalnya, `enable`, `disable`, `restart`).

Metode ini lebih disarankan karena lebih terintegrasi dengan sistem startup OpenWrt.
Berikut adalah contoh skrip init.d untuk bot Anda:
File: `/etc/init.d/telegram-bot`
```
#!/bin/sh /etc/rc.common

START=99
STOP=99

USE_PROCD=1
PROG_PATH="/www/assisten/bot/bot.py"
PROG_USER="root"
PROG_ARGS=""
PROG_PID_FILE="/var/run/bot_telegram.pid"

start_service() {
    procd_open_instance
    procd_set_param command "python3" "$PROG_PATH" $PROG_ARGS
    procd_set_param user "$PROG_USER"
    procd_set_param pidfile "$PROG_PID_FILE"
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}

stop_service() {
    [ -f "$PROG_PID_FILE" ] && kill $(cat "$PROG_PID_FILE")
    return 0
}
```
Setelah membuat file ini, kamu bisa mengaktifkan autostart di `terminal` dengan perintah:
```
dos2unix /etc/init.d/telegram-bot
chmod +x /etc/init.d/telegram-bot
/etc/init.d/telegram-bot enable
/etc/init.d/telegram-bot stop
/etc/init.d/telegram-bot start
```
<div align="center">
<p>Selesai! Sekarang bot Anda siap digunakan. Buka Telegram dan kirim perintah <code>/start</code> ke bot Anda.</p>
</div>
