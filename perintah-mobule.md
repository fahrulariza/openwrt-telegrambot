<h1>Asisten Bot Telegram sederhana untuk OpenWrt</h1>
<p>Kelola router OpenWrt Anda dengan mudah melalui bot Telegram!</p>
</div>

### Penjelasan setiap fungsi module

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
