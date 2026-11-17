import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
HELP_BOT_TOKEN = os.getenv("HELP_BOT_TOKEN", "").strip()

PROJECT_DIR = Path(__file__).resolve().parent
_session_dir = Path(os.getenv("SESSION_DIR", "sessions"))
SESSION_DIR = str(_session_dir if _session_dir.is_absolute() else PROJECT_DIR / _session_dir)
SESSION_FILE = os.getenv("SESSION_FILE", "").strip() or None
DB_FILE = os.getenv("DB_FILE", "bot_data.json")
OWNER_ID = None
RATE_LIMIT_DELAY    = 0.1
AUTO_SPAM_INTERVAL  = 3
MESSAGES_PER_BATCH  = 0


def load_replies():
    try:
        with open(PROJECT_DIR / "replies.txt", "r", encoding="utf-8") as f:
            data = [x.strip() for x in f if x.strip()]
            return data if data else ["سلام"]
    except OSError:
        return ["سلام"]

DEFAULT_REPLIES = load_replies()
