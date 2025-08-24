<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/9/92/Openwrt_Logo.svg" alt="OpenWrt Telegram Bot Logo" width="200"/>

![License](https://img.shields.io/github/license/fahrulariza/openwrt-telegrambot)
[![GitHub All Releases](https://img.shields.io/github/downloads/fahrulariza/openwrt-telegrambot/total)](https://github.com/fahrulariza/openwrt-telegrambot/releases)
![Total Commits](https://img.shields.io/github/commit-activity/t/fahrulariza/openwrt-telegrambot)
![Top Language](https://img.shields.io/github/languages/top/fahrulariza/openwrt-telegrambot)
[![Open Issues](https://img.shields.io/github/issues/fahrulariza/openwrt-telegrambot)](https://github.com/fahrulariza/openwrt-telegrambot/issues)

<h1>Simple Telegram Bot Assistant for OpenWrt</h1>
<p>Easily manage your OpenWrt router via Telegram bot!</p>
</div>

## 🚀 Key Features
- **Kontrol Penuh**: Jalankan perintah shell, pantau status sistem, dan kelola layanan langsung dari Telegram.
- **Interactive Interface**: Menggunakan Inline Keyboard untuk navigasi yang mudah tanpa mengetik perintah manual.
- **Instant Notifications**: Terima notifikasi real-time tentang status router Anda.
- **Secure Access**: Akses hanya diberikan kepada User ID yang telah disetujui.
- **Modular**: menambahkan dan menghapus module tanpa mengubah script utama hanya di folder `cmd`



### ⚙️ Installation File Structure
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
## 🛠️ File Structure Explanation
> - **/www/assisten/bot**: This is the main directory where all bot code resides.
> - folder **bot/**:
> 1. **cmd/**: This folder contains all command modules executable by the bot. Setiap file .py di sini (akses.py, status.py, dll.) adalah perintah terpisah yang akan dimuat secara dinamis oleh bot.py. File __init__.py kosong diperlukan agar Python mengenali cmd sebagai sebuah paket.
> 2. **bot.py**: The main bot script that runs all logic, handles Telegram connection, loads commands, and manages interaction.
> 3. **README.md**: Contains installation guide and project description.
> 4. **restart.sh**: Shell script to stop and restart the bot.
> 5. **run_bot.sh**: Main script to manage the bot lifecycle (start, stop, restart).
> 6. **akses.txt**: Text file containing list of authorized Telegram User IDs.
> 7. **token.txt**: Text file containing your bot API token from BotFather.
> 8. **.git/**: Direktori ini dibuat oleh Git untuk mengelola riwayat versi proyek.

This structure is clean, modular, and makes it easy to add, remove, or manage new commands without modifying the main script `bot.py` hanya uploda module ke folder `cmd`.

## 🛠️ Preparation
Required Tools
Sebelum memulai, pastikan telah menginstal tool berikut di OpenWrt :

through terminal in OpenWrt, follow the steps below

#### Update package list
```
opkg update
```
#### Install required packages
```
opkg install python3 python3-pip dos2unix wget git-http
```

> Tool Description
> 1. **python3:** The main programming language to run the bot.
> 2. **python3-pip:** Package manager to install required Python libraries.
> 3. **dos2unix:** To convert script file formats.
> 4. **wget:** To download files from the internet.
> 5. **git-http:** Used for easier installation process.

#### Install required Python libraries
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

## ⚙️ Installation Guide
Ikuti langkah-langkah di bawah ini untuk menginstal bot di router OpenWrt.
### Step 1: Clone Repository
Login to your OpenWrt router via `SSH` or `LuCI Terminal`, then run these commands to download the bot code and save it into the assisten folder at `/www/assisten/bot`:

```
mkdir /www/assisten
mkdir /www/assisten/bot
cd /www/assisten/
git clone https://github.com/fahrulariza/openwrt-telegrambot.git bot
```
or
1. Download manually [here](https://github.com/fahrulariza/openwrt-telegrambot/archive/refs/heads/master.zip)
2. Put all files into the folder `/www/asissten/bot/` structure can be seen above. then continue to Step 2

### Step 2: Configure Bot Token & User Access
Create a new Telegram bot via @BotFather and obtain its API token.

Create token.txt file in assisten/bot/ folder and put your token inside it.

```
echo "TOKEN_BOT_ANDA" > /www/assisten/bot/token.txt
```
Get your Telegram User ID from @userinfobot.

Create akses.txt file in the same folder and put your User ID inside it.

```
echo "ID_PENGGUNA_ANDA" > /www/assisten/bot/akses.txt
```
### Step 3: Install Python Libraries
Go to the bot directory and install all required libraries.

```
cd /www/assisten/bot
pip install -r requirements.txt
```
### Step 4: Run Preparation Script
This script will ensure all files have the correct execution permissions.
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
To ensure all files in cmd/ folder have correct format and permissions, run this again
```
cd /www/assisten/bot/cmd
dos2unix *.py
chmod +x *.py
```
### Step 5: Run Bot Manually
Use run_bot.sh script to start the bot. The bot will run in background.
```
/www/assisten/bot/run_bot.sh start
```

Alternative Method (Init Script)
A cleaner and recommended method in OpenWrt is to create `init.d` script khusus untuk bot Anda. Ini memberikan kontrol yang lebih baik (misalnya, `enable`, `disable`, `restart`).

This method is more recommended as it integrates better with OpenWrt startup system.
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
After creating this file, you can enable autostart in `terminal` with command:
```
dos2unix /etc/init.d/telegram-bot
chmod +x /etc/init.d/telegram-bot
/etc/init.d/telegram-bot enable
/etc/init.d/telegram-bot stop
/etc/init.d/telegram-bot start
```
<div align="center">
<p>Done! Now your bot is ready to use. Open Telegram and send the command <code>/start</code> ke bot Anda.</p>
</div>
