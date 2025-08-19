<h1>Asisten Bot Telegram sederhana untuk OpenWrt</h1>
<p>Kelola router OpenWrt Anda dengan mudah melalui bot Telegram!</p>
</div>

## Penjelasan setiap fungsi module

#### terminal.py
modul untuk mengeksekusi perintah terminal dan menampilkan hasilnya di chat telegram bot
`/terminal` di Telegram, seperti:
```
/terminal ps | grep bot
```
maka hasil yang dikirim berupa
```
31006 root     52676 S    /usr/bin/python3 /www/assisten/bot/bot.py
31155 root      1320 S    /bin/sh -c ps | grep bot
31158 root      1316 S    grep bot
```


#### cekmodule.py
modul untuk mengeksekusi perintah terminal dan menampilkan hasilnya di chat telegram bot
`/terminal` di Telegram, seperti:
```
/cekmodule
```
maka hasil yang dikirim berupa
```
📜 Daftar Modul yang Dimuat:

• Akses (v3.5.0) - `MENU`
• Cekmodule (v3.5.1) - `MENU`
• Dhcp_leases (v3.5.0) - `MENU`
• Force_update (v3.5.0) - `TEKS`
• Interface (v3.5.0) - `MENU`
• Openclash (v3.5.0) - `MENU`
• Reboot (v3.5.0) - `MENU`
• Reload_bot (v3.5.0) - `MENU`
• Status (v3.5.0) - `MENU`
• Terminal (v3.5.0) - `TEKS`
• Update (v3.5.0) - `MENU`
```


#### force_update.py
modul untuk mengeksekusi perintah terminal memaksa update apapun versinya. berguna untuk memperbaiki script yang rusak atau error

`/terminal` di Telegram, seperti:
```
/force_update
```
maka hasil yang dikirim berupa
```
🚨 Memaksa pembaruan perangkat saat ini...
```
