# 🤖 Telegram Userbot

<p align="center">
  <strong>A feature-rich Telegram Userbot built with Python</strong>
  <br>
  مدیریت حساب تلگرام با مجموعه‌ای از دستورات کاربردی، ابزارهای مدیریتی و قابلیت‌های قابل تنظیم
</p>

<p align="center">
  <a href="https://github.com/MrSudoXS/telegram-bot">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Termux-success?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

## 📌 معرفی پروژه | Introduction

**Telegram Userbot** یک پروژه Python برای مدیریت و خودکارسازی برخی فعالیت‌های حساب تلگرام است.

این پروژه با هدف ارائه مجموعه‌ای از ابزارها و دستورات کاربردی طراحی شده و قابلیت اجرا در محیط‌های مختلف از جمله Linux، Windows، Termux و Docker را دارد.

با استفاده از این پروژه می‌توانید از امکاناتی مانند دستورات مدیریتی، ابزارهای ضداسپم، مدیریت پیام‌ها و سیستم Session استفاده کنید.

> این پروژه یک Userbot است، نه یک Telegram Bot معمولی. برای اجرای آن از API حساب کاربری تلگرام استفاده می‌شود.

## ✨ امکانات | Features

- ⚡ مجموعه‌ای از دستورات کاربردی تلگرام
- 🛡️ ابزارهای مدیریت Spam
- 🔇 دستورات Mute و Ban
- 💬 سیستم مدیریت پیام‌ها
- 🆔 دستورات مرتبط با شناسه‌ها
- ⏱️ ابزارهای Reaction Time
- 💾 قابلیت ذخیره‌سازی اطلاعات
- 📚 سیستم راهنمای دستورات
- 🔐 مدیریت Session
- 🐳 پشتیبانی از Docker و Docker Compose
- 📱 قابلیت اجرا در Termux
- ⚙️ تنظیمات قابل مدیریت از طریق فایل `.env`

## 📋 فهرست مطالب | Table of Contents

- [پیش‌نیازها](#-پیشنیازها--requirements)
- [دریافت API تلگرام](#-دریافت-api-تلگرام)
- [نصب و راه‌اندازی](#-نصب-و-راهاندازی--installation)
  - [Linux](#-linux)
  - [Windows](#-windows)
  - [Termux](#-termux)
- [تنظیمات محیطی](#-تنظیمات-محیطی--environment-configuration)
- [اجرای پروژه با Docker](#-اجرای-پروژه-با-docker)
- [مدیریت Session](#-مدیریت-session)
- [دستورات](#-دستورات--commands)
- [رفع مشکلات رایج](#-رفع-مشکلات-رایج--troubleshooting)
- [امنیت](#-امنیت--security)
- [ساختار پروژه](#-ساختار-پروژه--project-structure)
---

## 📦 پیش‌نیازها | Requirements

قبل از نصب پروژه، موارد زیر را آماده کنید:

| ابزار | نسخه پیشنهادی |
|---|---|
| Python | 3.12 یا بالاتر |
| Git | نسخه جدید |
| pip | آخرین نسخه |
| Docker | در صورت استفاده از Docker |
| Docker Compose | در صورت استفاده از Docker |

همچنین به اطلاعات API تلگرام نیاز دارید:

- `API_ID`
- `API_HASH`

## 🔑 دریافت API تلگرام

برای دریافت اطلاعات API:

1. وارد وب‌سایت [my.telegram.org](https://my.telegram.org) شوید.
2. با حساب تلگرام خود وارد شوید.
3. وارد بخش **API Development Tools** شوید.
4. یک Application جدید ایجاد کنید.
5. مقادیر `API_ID` و `API_HASH` را دریافت کنید.

این اطلاعات محرمانه هستند و نباید در اختیار دیگران قرار بگیرند.

---

## 🚀 نصب و راه‌اندازی | Installation

ابتدا Repository را دریافت کنید:

```bash
git clone https://github.com/MrSudoXS/telegram-bot.git
cd telegram-bot
```

### 🐧 Linux

در توزیع‌های مبتنی بر Ubuntu و Debian:

```bash
sudo apt update

sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  build-essential \
  nano
```

ساخت محیط مجازی:

```bash
python3 -m venv .venv
```

فعال‌سازی محیط مجازی:

```bash
source .venv/bin/activate
```

به‌روزرسانی pip:

```bash
python -m pip install --upgrade pip
```

نصب وابستگی‌ها:

```bash
python -m pip install -r requirements.txt
```

ساخت فایل تنظیمات:

```bash
cp .env.example .env
```

ویرایش تنظیمات:

```bash
nano .env
```

اجرای پروژه:

```bash
python main.py
```

### 🪟 Windows

ابتدا Python 3.12 یا بالاتر و Git را نصب کنید.

PowerShell را باز کرده و دستورات زیر را اجرا کنید:

```powershell
git clone https://github.com/MrSudoXS/telegram-bot.git

cd telegram-bot
```

ساخت محیط مجازی:

```powershell
py -3.12 -m venv .venv
```

فعال‌سازی محیط:

```powershell
.\.venv\Scripts\Activate.ps1
```

در صورت محدودیت اجرای Script در PowerShell، برای همان پنجره:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

نصب وابستگی‌ها:

```powershell
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

ساخت فایل تنظیمات:

```powershell
Copy-Item .env.example .env
```

ویرایش فایل:

```powershell
notepad .env
```

اجرای پروژه:

```powershell
python main.py
```

### 📱 Termux

ابتدا بسته‌های موردنیاز را نصب کنید:

```bash
pkg update && pkg upgrade

pkg install git python clang make nano
```

دریافت پروژه:

```bash
git clone https://github.com/MrSudoXS/telegram-bot.git

cd telegram-bot
```

ساخت محیط مجازی:

```bash
python -m venv .venv
```

فعال‌سازی:

```bash
source .venv/bin/activate
```

نصب وابستگی‌ها:

```bash
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

ساخت تنظیمات:

```bash
cp .env.example .env

nano .env
```

اجرای Userbot:

```bash
python main.py
```

> توجه: برخی وابستگی‌های Python ممکن است در نسخه‌های مختلف Android و Termux نیازمند تنظیمات یا ابزارهای کامپایل بیشتری باشند.

---

## ⚙️ تنظیمات محیطی | Environment Configuration

پروژه از فایل `.env` برای نگهداری تنظیمات استفاده می‌کند.

ابتدا فایل نمونه را کپی کنید:

```bash
cp .env.example .env
```

ساختار تنظیمات:

```env
API_ID=12345678
API_HASH=your_api_hash

HELP_BOT_TOKEN=

SESSION_DIR=sessions
SESSION_FILE=
```

### توضیحات تنظیمات

| متغیر | توضیحات |
|---|---|
| `API_ID` | شناسه API تلگرام |
| `API_HASH` | کلید API تلگرام |
| `HELP_BOT_TOKEN` | توکن اختیاری ربات راهنما |
| `SESSION_DIR` | مسیر ذخیره Sessionها |
| `SESSION_FILE` | نام Session مورد استفاده |

مقادیر واقعی را با اطلاعات خود جایگزین کنید.

### دریافت توکن Help Bot

در صورت نیاز به قابلیت‌های ربات راهنما:

1. وارد تلگرام شوید.
2. به [@BotFather](https://t.me/BotFather) مراجعه کنید.
3. یک Bot جدید بسازید.
4. در صورت نیاز Inline Mode را فعال کنید.
5. توکن دریافت‌شده را در `HELP_BOT_TOKEN` قرار دهید.

این قابلیت اختیاری است.

---

## 🐳 اجرای پروژه با Docker

اگر Docker و Docker Compose نصب هستند، می‌توانید پروژه را بدون نصب مستقیم وابستگی‌های Python اجرا کنید.

ساخت فایل تنظیمات:

```bash
cp .env.example .env
```

مقادیر موردنیاز را وارد کنید:

```bash
nano .env
```

ساخت Image:

```bash
docker compose build
```

اجرای اولیه:

```bash
docker compose run --rm bot
```

در اجرای اولیه، مراحل ورود و ساخت Session را کامل کنید.

پس از ایجاد Session، نام آن را در فایل `.env` تنظیم کنید:

```env
SESSION_FILE=personal
```

نام بالا صرفاً نمونه است؛ از نام واقعی Session خود استفاده کنید.

اجرای پس‌زمینه:

```bash
docker compose up -d
```

مشاهده گزارش‌ها:

```bash
docker compose logs -f bot
```

توقف سرویس:

```bash
docker compose stop
```

اجرای مجدد:

```bash
docker compose start
```

حذف کانتینرها:

```bash
docker compose down
```

> اطلاعات Session باید در فضای ذخیره‌سازی پایدار نگهداری شوند. قبل از حذف یا بازسازی کانتینر، تنظیمات Volume در `docker-compose.yml` را بررسی کنید.

> Docker معمولاً به‌صورت مستقیم در Termux قابل استفاده نیست؛ برای Termux روش اجرای Python پیشنهاد می‌شود.

---

## 🔐 مدیریت Session | Session Management

پروژه از سیستم Session برای نگهداری اطلاعات احراز هویت تلگرام استفاده می‌کند.

در اولین اجرا:

1. برنامه فهرست Sessionهای موجود را نمایش می‌دهد.
2. برای ساخت Session جدید، گزینه `0` را انتخاب کنید.
3. یک نام برای Session انتخاب کنید.
4. شماره تلفن و کد ورود را در ترمینال وارد کنید.
5. در صورت فعال بودن تأیید دومرحله‌ای، رمز مربوطه را وارد کنید.

در اجراهای بعدی می‌توانید Session موردنظر را انتخاب کنید.

اگر فقط یک Session موجود باشد، برنامه ممکن است همان Session را به‌صورت خودکار انتخاب کند.

### نکات مهم

- فایل‌های Session را در اختیار دیگران قرار ندهید.
- فایل Session را در GitHub منتشر نکنید.
- از Session خود نسخه پشتیبان امن تهیه کنید.
- برای لغو دسترسی یک Session، از بخش **Devices** تلگرام استفاده کنید.

---

## 💻 دستورات | Commands

دستورات این Userbot با نقطه (`.`) شروع می‌شوند.

برای نمایش راهنمای دستورات:

```text
.راهنما
```

دسته‌بندی قابلیت‌های موجود در پروژه:

| دسته‌بندی | توضیحات |
|---|---|
| Basic Commands | دستورات پایه |
| Auto Spam | ابزارهای مرتبط با Spam |
| Enemy Commands | دستورات مرتبط با این بخش |
| Mute / Ban | مدیریت Mute و Ban |
| ID Commands | ابزارهای شناسه |
| Reaction Time | ابزارهای Reaction Time |
| Save Commands | قابلیت‌های ذخیره‌سازی |

برای مشاهده نام و عملکرد دقیق هر دستور، از راهنمای داخلی پروژه استفاده کنید.

---

## 🛠️ رفع مشکلات رایج | Troubleshooting

### مشکل نصب وابستگی‌ها

ابتدا مطمئن شوید محیط مجازی فعال است:

```bash
source .venv/bin/activate
```

سپس:

```bash
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

### خطای API_ID یا API_HASH

موارد زیر را بررسی کنید:

- مقادیر را بدون فاصله اضافی وارد کرده باشید.
- `API_ID` عددی باشد.
- `API_HASH` صحیح باشد.
- فایل `.env` در مسیر اصلی پروژه قرار داشته باشد.

### مشکل Session

اگر Session انتخاب‌شده پیدا نمی‌شود:

- مقدار `SESSION_DIR` را بررسی کنید.
- مقدار `SESSION_FILE` را بررسی کنید.
- از وجود فایل Session در مسیر موردنظر مطمئن شوید.
- مجوزهای دسترسی فایل‌ها را بررسی کنید.

### مشکل اجرای Docker

وضعیت سرویس‌ها:

```bash
docker compose ps
```

مشاهده گزارش‌ها:

```bash
docker compose logs -f bot
```

ساخت مجدد Image:

```bash
docker compose build --no-cache
```

### توقف برنامه

برای توقف اجرای مستقیم:

```text
Ctrl + C
```

برای توقف Docker:

```bash
docker compose stop
```

---

## 🔒 امنیت | Security

امنیت اطلاعات حساب تلگرام بسیار مهم است.

**هرگز موارد زیر را در GitHub منتشر نکنید:**

- فایل `.env`
- مقدار واقعی `API_HASH`
- توکن Help Bot
- فایل‌های Session
- رمزهای عبور
- اطلاعات خصوصی کاربران

فقط فایل `.env.example` را منتشر کنید.

اگر توکن ربات افشا شد، آن را از طریق BotFather باطل و جایگزین کنید.

اگر Session حساب تلگرام افشا شد، از بخش Devices نشست مربوطه را لغو کنید.

پروژه باید فقط با رعایت قوانین تلگرام و قوانین قابل‌اعمال استفاده شود.

---

## 📁 ساختار پروژه | Project Structure

```text
telegram-bot/
│
├── commands/
│   ├── __init__.py
│   ├── autospam_commands.py
│   ├── basic_commands.py
│   ├── command_registry.py
│   ├── enemy_commands.py
│   ├── id_commands.py
│   ├── mute_ban_commands.py
│   ├── reaction_time_commands.py
│   ├── save_commands.py
│   └── spam_commands.py
│
├── handlers/
│   ├── __init__.py
│   ├── help_bot.py
│   └── message_handler.py
│
├── utils/
│   ├── __init__.py
│   ├── database.py
│   ├── filters.py
│   ├── helpers.py
│   └── state.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── config.py
├── main.py
├── replies.txt
├── requirements.txt
└── README.md
```

---

## 🤝 مشارکت در پروژه | Contributing

از مشارکت در بهبود پروژه استقبال می‌شود.

برای پیشنهاد قابلیت جدید یا گزارش مشکل:

1. Repository را Fork کنید.
2. یک Branch جدید بسازید.
3. تغییرات موردنظر را اعمال کنید.
4. تغییرات را Commit کنید.
5. یک Pull Request ایجاد کنید.

نمونه:

```bash
git checkout -b feature/new-command

git add .

git commit -m "Add new command"

git push origin feature/new-command
```

---

## 📄 مجوز | License

مجوز پروژه باید مطابق فایل LICENSE در Repository تعیین شود.

در صورت نبود فایل LICENSE، وضعیت مجوز استفاده و بازنشر پروژه هنوز مشخص نشده است.

---

## ⭐ حمایت از پروژه

اگر این پروژه برای شما مفید بود، می‌توانید با Star کردن Repository از توسعه آن حمایت کنید.

<p align="center">
  <a href="https://github.com/MrSudoXS/telegram-bot">
    <img src="https://img.shields.io/badge/⭐%20Star%20this%20repository-GitHub-yellow?style=for-the-badge" alt="Star Repository">
  </a>
</p>

<p align="center">
  <strong>Made with ❤️ and Python</strong>
  <br>
  <a href="https://github.com/MrSudoXS">MrSudoXS</a>
</p>
