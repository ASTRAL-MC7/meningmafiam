# 🎭 Mafia Bot — O'zbek tilida

Telegram uchun to'liq Mafia o'yin boti. 15+ rol, inline tugmalar, admin panel.

---

## 🚀 Replit'da Sozlash

### 1. Token olish
- [@BotFather](https://t.me/BotFather) ga boring
- `/newbot` buyrug'ini yuboring
- Bot nomini va username'ini kiriting
- Token oling (masalan: `7123456789:AAF...`)

### 2. Replit Secrets
Replit loyihasida **Secrets** (🔒) bo'limiga boring va qo'shing:
```
Key:   BOT_TOKEN
Value: (BotFather'dan olgan tokeningiz)
```

### 3. Ishga tushirish
`main.py` ni ishga tushiring. Bot tayyor!

### 4. UptimeRobot (ixtiyoriy)
Bot doim ishlashi uchun [UptimeRobot](https://uptimerobot.com) da:
- Monitor type: HTTP(s)
- URL: `https://YOUR-REPL-NAME.YOUR-USERNAME.repl.co`
- Interval: 5 daqiqa

---

## 🎮 O'yin Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/yangioyun` | Yangi o'yin yaratish |
| `/qoshilish` | O'yinga qo'shilish |
| `/boshlash` | O'yinni boshlash |
| `/toxtash` | O'yinni bekor qilish |
| `/oyinchilar` | O'yinchilar ro'yxati |
| `/yordam` | Yordam |

## 🛠 Admin Buyruqlari (faqat ID: 5523761749)

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin paneli |
| `/users` | Foydalanuvchilar soni |
| `/xabar <matn>` | Hammaga xabar yuborish |

---

## 🎭 Rollar (15+)

| Rol | Emoji | Jamoa | Tavsif |
|-----|-------|-------|--------|
| Mafia | 🔴 | Mafia | Tungi o'ldirish |
| Don | ⚫ | Mafia | Mafia boshlig'i, Detektiv ko'rmaydi |
| Detektiv | 🟡 | Fuqaro | Tungi tekshirish |
| Shifokor | 🟢 | Fuqaro | Tungi davolash |
| Sheriff | 🟠 | Fuqaro | Mafiachini otadi |
| Fahisha | 💜 | Fuqaro | Tungi bloklash |
| Jurnalist | 🔵 | Fuqaro | Aniq rol aniqlash |
| Maniak | 🩸 | Neytral | Yolg'iz o'ldiradi |
| Farishta | 👼 | Fuqaro | Bir marta tiriladi |
| Portlovchi | 💣 | Fuqaro | O'lsa qo'shnisini ham o'ldiradi |
| Joker | 🃏 | Neytral | Har tun rol o'zgaradi |
| Agent | 🕵️ | Fuqaro | Ikkita tekshirish |
| Sehrgar | 🧙 | Fuqaro | Ovozni bloklaydi |
| Qahramon | ⚔️ | Fuqaro | Mafiachiga hujum |
| Fuqaro | 👤 | Fuqaro | Oddiy fuqaro |

---

## 📁 Fayl Tuzilishi
```
mafia_bot/
├── main.py         # Kirish nuqtasi (Replit uchun)
├── bot.py          # Bot logikasi, buyruqlar
├── game.py         # O'yin mexanikasi, rollar
├── database.py     # SQLite foydalanuvchi bazasi
├── config.py       # Token va admin ID
├── keep_alive.py   # Replit uchun web server
├── requirements.txt
└── .replit
```
