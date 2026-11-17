# تلگرام یوزربات

سلام! این راهنما از گرفتن اطلاعات تلگرام تا اجرای بات و خاموش‌کردنش همراهته. دستورها رو به‌ترتیب انجام بده و آدرس نمونه‌ی GitHub رو با آدرس ریپوی خودت عوض کن.

## ۱. چیزهایی که لازم داری

- Git
- Python 3.12 یا بالاتر برای اجرای مستقیم
- Docker و Docker Compose برای روش Docker
- `API_ID` و `API_HASH` حساب تلگرام

برای گرفتن دو مقدار API به [my.telegram.org](https://my.telegram.org) برو، وارد حسابت شو و از بخش **API Development Tools** یک برنامه بساز. مقدارها رو نگه دار؛ مرحله‌ی بعد لازم می‌شن.

## ۲. تنظیم `.env`

فایل `.env` تنظیمات خصوصی خودته. از فایل نمونه کپی بگیر:

Linux و Termux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

فایل `.env` رو باز کن و مقدارهای خودت رو وارد کن:

```env
API_ID=12345678
API_HASH=مقدار-api-hash-خودت
HELP_BOT_TOKEN=
SESSION_DIR=sessions
SESSION_FILE=
```

`API_ID` رو با عدد خودت و `API_HASH` رو با مقدار دریافتی از my.telegram.org جایگزین کن. اگر منوی دکمه‌ای راهنما رو می‌خوای، در `@BotFather` بات بساز، Inline Mode رو فعال کن و توکنش رو در `HELP_BOT_TOKEN` بذار. این توکن اختیاریه.

بار اول `SESSION_FILE` رو خالی بذار. بعد از ساخت سشن، اگر اجرای Docker در پس‌زمینه می‌خوای، اسم سشن رو بدون `.session` همین‌جا بنویس.

## ۳. ورود اول و اجراهای بعدی

در اولین اجرا، برنامه فهرست سشن‌ها رو نشان می‌ده. `0` رو بزن، برای سشن یک اسم انتخاب کن و ورود تلگرام رو کامل کن. شماره، کد ورود و رمز دومرحله‌ای رو فقط در ترمینال خودت وارد کن.

برای اجراهای بعدی، سشن رو از فهرست انتخاب کن. اگر فقط یک سشن موجود باشه، برنامه خودش همون رو انتخاب می‌کنه. برای توقف اجرای مستقیم، `Ctrl+C` بزن.

## Termux

Termux رو باز کن و پروژه رو دریافت کن:

```bash
pkg update
pkg install git python clang make nano
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

محیط Python و وابستگی‌ها رو نصب کن:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

حالا `.env` رو بساز و تنظیم کن:

```bash
cp .env.example .env
nano .env
```

اجرا:

```bash
python main.py
```

برای اجرای دوباره، از پوشه‌ی پروژه این‌ها رو بزن:

```bash
source .venv/bin/activate
python main.py
```

برای توقف `Ctrl+C` بزن. اگر نصب `TgCrypto` روی نسخه‌ی فعلی Termux انجام نشد، از Linux یا Docker استفاده کن.

## Linux

در Ubuntu یا Debian:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential nano
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py
```

برای اجرای دوباره، در پوشه‌ی پروژه محیط رو فعال و بات رو اجرا کن:

```bash
source .venv/bin/activate
python main.py
```

برای توقف `Ctrl+C` بزن.

## Windows

Git و Python 3.12 یا بالاتر رو نصب کن. بعد PowerShell رو باز کن:

```powershell
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python main.py
```

برای اجرای دوباره:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

برای توقف `Ctrl+C` بزن. اگر PowerShell جلوی فعال‌سازی محیط رو گرفت، فقط برای پنجره‌ی فعلی اجازه بده:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Docker

Docker و Docker Compose رو نصب کن. Docker معمولاً مستقیم روی Termux اجرا نمی‌شه؛ در Termux از روش Python استفاده کن.

Linux:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
cp .env.example .env
nano .env
docker compose build
docker compose run --rm bot
```

Windows PowerShell:

```powershell
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
Copy-Item .env.example .env
notepad .env
docker compose build
docker compose run --rm bot
```

در اجرای اول، سشن رو با انتخاب `0` بساز و ورود رو کامل کن. بعد `.env` رو باز کن و اسم سشن رو بدون پسوند در `SESSION_FILE` بنویس. مثلاً:

```env
SESSION_FILE=personal
```

اجرای پس‌زمینه و دیدن گزارش:

```bash
docker compose up -d
docker compose logs -f bot
```

توقف موقت، اجرای دوباره و خاموش‌کردن:

```bash
docker compose stop
docker compose start
docker compose down
```

`down` کانتینر رو حذف می‌کنه، اما فایل‌های سشن روی کامپیوتر باقی می‌مونن. برای خروج کامل حساب، نشست تلگرام رو از بخش **Devices** هم لغو کن.

## دستورهای بات

دستورها با نقطه شروع می‌شن. منوی راهنما:

```text
.راهنما
```

## انتشار در GitHub

در GitHub یک ریپازیتوری خالی بساز و آدرسش رو جای `USERNAME/REPOSITORY` در دستورهای بالا بذار. بعد در پوشه‌ی پروژه:

```bash
git init
git add .
git status --short
```

قبل از انتشار مطمئن شو `.env`، `sessions/`، دیتابیس‌ها و `.venv/` در فهرست فایل‌ها نیستند. بعد:

```bash
git commit -m "Add Telegram userbot"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

فقط `.env.example` رو منتشر کن. اگر توکن یا سشن جایی لو رفت، توکن رو عوض کن و نشست تلگرام رو لغو کن.

## English quick start

Get `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org). Clone the repository, create `.env` from `.env.example`, enter your values, then install and run:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate it with `.\.venv\Scripts\Activate.ps1`. On the first run, choose `0` to create a Telegram session. Stop with `Ctrl+C`.

For Docker, run `docker compose build`, then `docker compose run --rm bot` to create and log into a session. Set `SESSION_FILE` in `.env`, then use `docker compose up -d`. Stop with `docker compose stop`; remove the container with `docker compose down`.

All commands start with a dot. Send `.راهنما` for the help menu. Star the repo if it helped you!
