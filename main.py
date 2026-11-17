import asyncio
import json
import os
import sqlite3
import sys
from pyrogram import Client
from config import API_ID, API_HASH, HELP_BOT_TOKEN, SESSION_DIR
from handlers import setup_message_handler, time_name_task
from commands import setup_all_commands
from handlers.help_bot import setup_help_bot
from utils import state
from utils.database import db


def ensure_session_folder() -> None:
    os.makedirs(SESSION_DIR, exist_ok=True)


def find_sessions() -> list[str]:
    if not os.path.isdir(SESSION_DIR):
        return []
    return sorted(os.path.splitext(f)[0] for f in os.listdir(SESSION_DIR) if f.endswith(".session"))


SESSION_META_EXT = ".meta.json"


def prompt_owner_id() -> int | None:
    while True:
        owner_id_text = input("Please enter the numeric user ID: ").strip()
        if not owner_id_text:
            return None
        if owner_id_text.lstrip("-").isdigit():
            return int(owner_id_text)
        print("Please enter a valid numeric user ID.")


def save_session_meta(session_path: str, owner_id: int | None) -> None:
    if owner_id is None:
        return
    meta_path = f"{session_path}{SESSION_META_EXT}"
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"owner_id": int(owner_id)}, f)
    except Exception:
        pass


def load_session_meta(session_path: str) -> int | None:
    meta_path = f"{session_path}{SESSION_META_EXT}"
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("owner_id")) if data.get("owner_id") is not None else None
    except Exception:
        return None


async def detect_session_owner(session_path: str) -> int | None:
    app = Client(session_path, api_id=API_ID, api_hash=API_HASH)
    try:
        await app.start()
        me = await app.get_me()
        return int(me.id) if me else None
    except Exception:
        return None
    finally:
        try:
            await app.stop()
        except Exception:
            pass


async def load_session_owner(session_path: str) -> int | None:
    owner_id = load_session_meta(session_path)
    if owner_id is not None:
        return owner_id

    owner_id = await detect_session_owner(session_path)
    if owner_id is not None:
        save_session_meta(session_path, owner_id)
        return owner_id

    owner_id = prompt_owner_id()
    if owner_id is not None:
        save_session_meta(session_path, owner_id)
    return owner_id


async def create_session(name: str | None = None) -> str | None:
    if not name:
        name = input("Name of the new session: ").strip()
    if not name:
        return None

    name = name.strip()
    if name.endswith(".session"):
        name = os.path.splitext(name)[0]
    if name in {".", ".."} or "/" in name or "\\" in name:
        print("Use a session name without directory paths.")
        return None

    session_path = os.path.join(SESSION_DIR, name)
    session_file = f"{session_path}.session"
    if os.path.exists(session_file):
        print(f"Session '{name}' already exists; using it.")
        return session_path

    app = Client(session_path, api_id=API_ID, api_hash=API_HASH)
    owner_id = None
    try:
        await app.start()
        me = await app.get_me()
        owner_id = int(me.id) if me else None
    except Exception as error:
        print(f"Session login failed: {error}")
        return None
    finally:
        try:
            await app.stop()
        except Exception:
            pass

    if owner_id is None:
        print("Could not read the owner ID from the logged-in account.")
        return None

    save_session_meta(session_path, owner_id)
    print(f"Session created: {name}")
    return session_path


async def choose_session() -> str | None:
    ensure_session_folder()
    sessions = find_sessions()
    configured_session = os.getenv("SESSION_FILE", "").strip()
    if configured_session.endswith(".session"):
        configured_session = os.path.splitext(configured_session)[0]

    if not sys.stdin.isatty():
        if configured_session in sessions:
            return os.path.join(SESSION_DIR, configured_session)
        if len(sessions) == 1:
            return os.path.join(SESSION_DIR, sessions[0])
        print("Set SESSION_FILE to an existing session for non-interactive startup.")
        return None

    print("\n Sessions:")
    if sessions:
        for i, s in enumerate(sessions):
            print(f"{i+1}. {s}")
    else:
        print("No sessions found.")

    print("\n0. Create New Session")
    default = f" [default: {configured_session}]" if configured_session in sessions else ""
    choice = input(f"Session number or name{default}: ").strip()

    if not choice:
        if configured_session in sessions:
            return os.path.join(SESSION_DIR, configured_session)
        if len(sessions) == 1:
            return os.path.join(SESSION_DIR, sessions[0])
        if not sessions and configured_session:
            return await create_session(configured_session)
        print("Choose a session number/name, or 0 to create one.")
        return None

    if choice == "0":
        return await create_session()

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(sessions):
            return os.path.join(SESSION_DIR, sessions[index])

    if choice.endswith(".session"):
        choice = os.path.splitext(choice)[0]
    if choice in sessions:
        return os.path.join(SESSION_DIR, choice)

    return await create_session(choice)


def ensure_session(session_name: str) -> bool:
    path = session_name if session_name.endswith(".session") else f"{session_name}.session"
    if not os.path.exists(path):
        return True

    connection = sqlite3.connect(path)
    try:
        connection.execute("SELECT number FROM version").fetchone()
        return True
    except sqlite3.OperationalError as error:
        print(f"Session file validation failed; file left unchanged: {error}")
        return False
    finally:
        connection.close()


async def get_session() -> str | None:
    session_name = await choose_session()
    if not session_name:
        print("No session selected. Exiting.")
        return None
    return session_name


async def main():
    if API_ID <= 0 or not API_HASH:
        raise RuntimeError("Set valid API_ID and API_HASH environment variables before starting the bot.")

    session_name = await get_session()
    if not session_name:
        return

    if not ensure_session(session_name):
        return

    owner_id = await load_session_owner(session_name)
    if owner_id is None:
        print("Owner ID is required to run the bot. Exiting.")
        return
    session_db_file = f"{session_name}.db.json"
    db.set_db_file(session_db_file)
    state.reload()

    state.set_owner_id(owner_id)
    state.set_session_name(session_name)

    app = Client(session_name, api_id=API_ID, api_hash=API_HASH)
    help_app = None

    setup_message_handler(app)
    setup_all_commands(app)

    try:
        async with app:
            me = await app.get_me()
            actual_owner_id = int(me.id)
            if state.OWNER_ID != actual_owner_id:
                print("Session owner metadata did not match the logged-in account; updating it.")
                state.set_owner_id(actual_owner_id)
                save_session_meta(session_name, actual_owner_id)
            from utils import strip_time_suffix
            state.BASE_NAME = strip_time_suffix(me.first_name or "")
            print(f"Connected | {state.BASE_NAME} (@{me.username})")
            print("Send .راهنما to open the help menu")

            if HELP_BOT_TOKEN:
                help_app = Client(
                    "help-menu",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    bot_token=HELP_BOT_TOKEN,
                    in_memory=True,
                )
                setup_help_bot(help_app, actual_owner_id)
                try:
                    await help_app.start()
                    bot_identity = await help_app.get_me()
                    state.HELP_BOT_USERNAME = bot_identity.username
                    state.HELP_BOT_CLIENT = help_app
                    state.HELP_BOT_START_ERROR = None
                    print(f"Helper bot is ready: @{bot_identity.username}")
                except Exception as error:
                    safe_error = str(error).replace(HELP_BOT_TOKEN, "<redacted>")
                    state.HELP_BOT_START_ERROR = f"{error.__class__.__name__}: {safe_error}"
                    print(
                        "Help bot could not start; "
                        f"{state.HELP_BOT_START_ERROR}. Userbot commands remain active."
                    )
                    if help_app.is_connected:
                        await help_app.stop()
                    help_app = None
                    state.HELP_BOT_CLIENT = None
                    state.HELP_BOT_USERNAME = None
            else:
                print("Set HELP_BOT_TOKEN in .env to enable the clickable help menu.")

            time_task = asyncio.create_task(time_name_task(app))
            try:
                await asyncio.Event().wait()
            finally:
                time_task.cancel()
                if help_app is not None:
                    await help_app.stop()
                    state.HELP_BOT_CLIENT = None
    except Exception:
        if help_app is not None and help_app.is_connected:
            await help_app.stop()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped")
    except Exception as e:
        print(f"Error: {e}")
