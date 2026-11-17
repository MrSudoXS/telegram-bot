import os
import re
import logging
from pyrogram import filters
from pyrogram.enums import ParseMode
from utils import owner_command, edit_or_reply
from commands.command_registry import (
    CMD_SAVE,
    MSG_SAVE_NEEDS_REPLY,
    MSG_SAVE_SUCCEEDED,
    MSG_SAVE_FAILED,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAVED_MEDIA_DIR = os.path.join(PROJECT_ROOT, "saved_media")
logger = logging.getLogger(__name__)

MESSAGE_LINK_RE = re.compile(
    r"^(?:https?://)?t\.me/(c/)?([\w\-]+)/([0-9]+)(?:\?.*)?$",
    re.IGNORECASE,
)


def _ensure_saved_media_dir():
    os.makedirs(SAVED_MEDIA_DIR, exist_ok=True)
    return SAVED_MEDIA_DIR


def _download_filename(message):
    msg_id = message.id
    if message.photo:
        return f"photo_{msg_id}.jpg"
    if message.video:
        return getattr(message.video, "file_name", f"video_{msg_id}.mp4")
    if message.animation:
        return getattr(message.animation, "file_name", f"animation_{msg_id}.mp4")
    if message.sticker:
        return f"sticker_{msg_id}.webp"
    if message.document:
        return getattr(message.document, "file_name", f"document_{msg_id}.bin")
    if message.video_note:
        return f"video_note_{msg_id}.mp4"
    if message.audio:
        return getattr(message.audio, "file_name", f"audio_{msg_id}.ogg")
    if message.voice:
        return getattr(message.voice, "file_name", f"voice_{msg_id}.ogg")
    return f"media_{msg_id}"


async def _save_media_to_project_and_send(client, message):
    _ensure_saved_media_dir()
    filename = _download_filename(message)
    file_path = os.path.join(SAVED_MEDIA_DIR, filename)
    downloaded_path = None

    try:
        downloaded_path = await client.download_media(message, file_name=file_path)
        if not downloaded_path or not os.path.exists(downloaded_path):
            return None

        if message.photo:
            return await client.send_photo(
                "me",
                photo=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
        if message.video:
            return await client.send_video(
                "me",
                video=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
        if message.animation:
            return await client.send_animation(
                "me",
                animation=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
        if message.sticker:
            return await client.send_sticker(
                "me",
                sticker=downloaded_path,
                disable_notification=True,
            )
        if message.document:
            return await client.send_document(
                "me",
                document=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
        if message.video_note:
            return await client.send_video_note(
                "me",
                video_note=downloaded_path,
                disable_notification=True,
            )
        if message.audio:
            return await client.send_audio(
                "me",
                audio=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
        if message.voice:
            return await client.send_voice(
                "me",
                voice=downloaded_path,
                caption=message.caption,
                disable_notification=True,
            )
    except Exception:
        return None
    finally:
        if downloaded_path and os.path.exists(downloaded_path):
            try:
                os.remove(downloaded_path)
            except Exception:
                pass

    return None


async def _save_text_fallback(client, message):
    """Last resort for protected or migrated/scam supergroups."""
    text = message.text or message.caption
    if text:
        return await client.send_message(
            "me", text, parse_mode=ParseMode.DISABLED, disable_notification=True
        )
    return None


async def _resolve_link_message(client, link):
    if not link:
        return None

    match = MESSAGE_LINK_RE.search(link)
    if not match:
        return None

    is_internal_link, chat_part, message_id = match.groups()
    if is_internal_link:
        chat_id = int(f"-100{chat_part}")
    elif chat_part.isdigit():
        chat_id = int(chat_part)
    else:
        chat_id = f"@{chat_part}"

    try:
        return await client.get_messages(chat_id, int(message_id))
    except Exception:
        return None


def setup_save_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_SAVE))
    async def save_cmd(client, message):
        target = message.reply_to_message
        if not target:
            parts = (message.text or "").strip().split(maxsplit=1)
            if len(parts) == 2:
                link = parts[1].strip()
                try:
                    target = await client.get_messages(link)
                except Exception:
                    target = None
                if isinstance(target, (list, tuple)) and target:
                    target = target[0]
                if not target:
                    target = await _resolve_link_message(client, link)

        if not target:
            await edit_or_reply(message, MSG_SAVE_NEEDS_REPLY)
            return

        saved = False

        try:
            await target.copy("me")
            saved = True
        except Exception:
            pass

        if not saved:
            try:
                await client.copy_message("me", target.chat.id, target.id)
                saved = True
            except Exception:
                saved = False

        if not saved:
            saved_message = await _save_media_to_project_and_send(client, target)
            saved = saved_message is not None

        if not saved:
            try:
                await client.forward_messages("me", target.chat.id, target.id)
                saved = True
            except Exception:
                saved = False

        if not saved:
            try:
                saved = (await _save_text_fallback(client, target)) is not None
            except Exception:
                saved = False

        if saved:
            await edit_or_reply(message, MSG_SAVE_SUCCEEDED)
        else:
            await edit_or_reply(message, MSG_SAVE_FAILED)
