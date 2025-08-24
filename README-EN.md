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


klik disini untuk petunjuk berbahasa indonesia [here](https://github.com/fahrulariza/openwrt-telegrambot/blob/master/README.md)

## 🚀 Key Features
- **Full Control**: Run shell commands, monitor system status, and manage services directly from Telegram.
- **Interactive Interface**: Use an inline keyboard for easy navigation without typing commands manually.
- **Instant Notifications**: Receive real-time notifications about your router's status.
- **Secure Access**: Access is only granted to approved user IDs.
- **Modular**: Add and remove modules without changing the main script, just in the `cmd` folder.



### ⚙️ Installation File Structure
```
/www/assisten/
        ├── bot/
        │   ├── cmd/       <<<<<<<<<<< the main folder contains the command module
        │   │   ├── __init__.py
        │   │   ├── akses.py
        │   │   ├── dhcp_leases.py
        │   │   ├── interface.py
        │   │   ├── openclash.py
        │   │   ├── reboot.py
        │   │   ├── reload_bot.py
        │   │   ├── status.py
        │   │   └── update.py
        │   ├── bot.py <<<<<<<<<<<<<<< main script to receive and execute commands.
        │   ├── README.md
        │   ├── restart.sh
        │   ├── run_bot.sh  <<<<<<<<<< execution script to run bot.py
        │   ├── akses.txt <<<<<<<<<<<< contains the ID that will be able to access the bot commands
        │   └── token.txt <<<<<<<<<<<< contains the bot token to be used
        └── .git/
```
## 🛠️ File Structure Explanation
> - **/www/assisten/bot**: This is the main directory where all bot code resides.
> - folder **bot/**:
> 1. **cmd/**: This folder contains all command modules executable by the bot. Each .py file here (access.py, status.py, etc.) is a separate command that will be dynamically loaded by bot.py. An empty __init__.py file is required for Python to recognize cmd as a package.
> 2. **bot.py**: The main bot script that runs all logic, handles Telegram connection, loads commands, and manages interaction.
> 3. **README.md**: Contains installation guide and project description.
> 4. **restart.sh**: Shell script to stop and restart the bot.
> 5. **run_bot.sh**: Main script to manage the bot lifecycle (start, stop, restart).
> 6. **akses.txt**: Text file containing list of authorized Telegram User IDs.
> 7. **token.txt**: Text file containing your bot API token from BotFather.
> 8. **.git/**: This directory is created by Git to manage the project's version history.

This structure is clean, modular, and makes it easy to add, remove, or manage new commands without modifying the main script `bot.py` just upload the module to the `cmd` folder.

## 🛠️ Preparation
Required Tools
Before starting, make sure you have installed the following tools in OpenWrt:

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
Follow the steps below to install the bot on an OpenWrt router.
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
A cleaner and recommended method in OpenWrt is to create a custom `init.d` script for your bot. This provides more fine-grained control (e.g., `enable`, `disable`, `restart`).

This method is more recommended as it integrates better with OpenWrt startup system.
Here's an example of an init.d script for your bot:
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
<p>Done! Now your bot is ready to use. Open Telegram and send the command <code>/start</code> to your bot.</p>
</div>
