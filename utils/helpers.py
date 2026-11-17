import asyncio
import html
import logging
import re
from html.parser import HTMLParser
from datetime import datetime, timedelta, timezone
from pyrogram.enums import ParseMode
from pyrogram.raw import functions
from config import RATE_LIMIT_DELAY
from utils.state import state
from commands.command_registry import RESPONSE_SIGNATURE

logger = logging.getLogger(__name__)


class _SafeHTML(HTMLParser):
    _simple_tags = {"b", "strong", "i", "em", "u", "s", "code", "pre", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self.open_tags = []

    def handle_starttag(self, tag, attrs):
        if tag in self._simple_tags:
            self.parts.append(f"<{tag}>")
            self.open_tags.append(tag)
        elif tag == "a":
            href = dict(attrs).get("href", "")
            if re.fullmatch(r"tg://user\?id=\d+", href):
                self.parts.append(f'<a href="{html.escape(href, quote=True)}">')
                self.open_tags.append(tag)
            else:
                self.parts.append(html.escape(self.get_starttag_text(), quote=False))
        else:
            self.parts.append(html.escape(self.get_starttag_text(), quote=False))

    def handle_endtag(self, tag):
        if tag in self.open_tags:
            self.parts.append(f"</{tag}>")
            self.open_tags.remove(tag)
        elif tag in self._simple_tags or tag == "a":
            self.parts.append(html.escape(f"</{tag}>", quote=False))
        else:
            self.parts.append(html.escape(f"</{tag}>", quote=False))

    def handle_data(self, data):
        self.parts.append(html.escape(data, quote=False))

    def handle_entityref(self, name):
        self.parts.append(html.escape(html.unescape(f"&{name};"), quote=False))

    def handle_charref(self, name):
        self.parts.append(html.escape(html.unescape(f"&#{name};"), quote=False))

    def handle_comment(self, data):
        self.parts.append(html.escape(f"<!--{data}-->", quote=False))


def format_response(text: str) -> str:
    """Style command feedback with selective quotes and a compact signature."""
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    first_line, separator, remaining = text.partition("\n")
    if first_line and not re.search(r"</?(?:b|strong)(?:\s|>)", first_line):
        first_line = f"<b>{first_line}</b>"
    if separator:
        text = f"{first_line}\n<blockquote>{remaining}</blockquote>"
    else:
        text = first_line
    parser = _SafeHTML()
    parser.feed(text)
    parser.close()
    for tag in reversed(parser.open_tags):
        parser.parts.append(f"</{tag}>")
    safe_text = "".join(parser.parts)
    return f"{safe_text} <b>{RESPONSE_SIGNATURE}</b>"

_BOLD = str.maketrans("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")
_ITALIC = {
    **{ord(chr(i + 65)): 0x1D468 + i for i in range(26)},
    **{ord(chr(i + 97)): 0x1D482 + i for i in range(26)},
}


def bold_time(t: str) -> str:
    return t.translate(_BOLD)


def italic_text(text: str) -> str:
    return text.translate(_ITALIC)


def stylish_time(t: str) -> str:
    return f"{bold_time(t)} 𒉭"


def _display_name_from_user(user):
    if not user:
        return None
    first_name = getattr(user, "first_name", None) or ""
    last_name = getattr(user, "last_name", None) or ""
    display = f"{first_name} {last_name}".strip()
    if display:
        return display
    return getattr(user, "username", None)


def _display_name_from_entity_text(message, entity):
    text = getattr(message, "text", None)
    if not text:
        return None
    offset = getattr(entity, "offset", None)
    length = getattr(entity, "length", None)
    if offset is None or length is None:
        return None
    return text[offset : offset + length]


def strip_time_suffix(name: str) -> str:
    pattern = re.compile(r"(?:\s+IRAN)?\s+[0-9𝟎-𝟗]{2}:[0-9𝟎-𝟗]{2}\s+𒉭$|\s+𒉭$")
    return pattern.sub("", name).rstrip()


def iran_time() -> str:
    tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(tz).strftime("%H:%M")


async def get_user_info(message):
    if message.reply_to_message:
        r = message.reply_to_message
        uid = None
        username = None
        display_name = None

        if r.from_user:
            uid = r.from_user.id
            username = r.from_user.username
            display_name = _display_name_from_user(r.from_user)
        elif getattr(r, "forward_from", None):
            uid = r.forward_from.id
            username = r.forward_from.username
            display_name = _display_name_from_user(r.forward_from)
        elif getattr(r, "sender_chat", None) and getattr(r.sender_chat, "type", None) == "private":
            uid = r.sender_chat.id
            username = getattr(r.sender_chat, "username", None)
            display_name = _display_name_from_user(r.sender_chat)

        if uid:
            return {"uid": uid, "username": username, "display_name": display_name, "found": True}

        # support text mentions without username in the replied message
        entities = getattr(r, "entities", None) or []
        for entity in entities:
            user_id = getattr(entity, "user_id", None)
            username = None
            display_name = None
            if user_id is None:
                user = getattr(entity, "user", None)
                user_id = getattr(user, "id", None)
                username = getattr(user, "username", None) if user is not None else None
                display_name = _display_name_from_user(user)
            else:
                display_name = _display_name_from_entity_text(r, entity)

            if user_id is not None:
                return {"uid": int(user_id), "username": username, "display_name": display_name, "found": True}

    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1]
        if arg.lstrip("-").isdigit():
            return {"uid": int(arg), "username": None, "display_name": None, "found": True}
        if arg.startswith("@"):
            username = arg[1:]
            try:
                user = await message._client.get_users(username)
                return {
                    "uid": user.id,
                    "username": username,
                    "display_name": _display_name_from_user(user),
                    "found": True,
                }
            except Exception:
                return {"uid": None, "username": username, "display_name": None, "found": False}

    # support text mentions in the command message itself
    entities = getattr(message, "entities", None) or []
    for entity in entities:
        user_id = getattr(entity, "user_id", None)
        username = None
        display_name = None
        if user_id is None:
            user = getattr(entity, "user", None)
            user_id = getattr(user, "id", None)
            username = getattr(user, "username", None) if user is not None else None
            display_name = _display_name_from_user(user)
        else:
            display_name = _display_name_from_entity_text(message, entity)

        if user_id is not None:
            return {"uid": int(user_id), "username": username, "display_name": display_name, "found": True}

    return {"uid": None, "username": None, "display_name": None, "found": False}


async def parse_user_targets(message):
    text = (message.text or "").strip()
    parts = text.split()
    args = parts[1:]
    targets = []
    seen = set()

    for arg in args:
        if not arg:
            continue
        if arg.lstrip("-").isdigit():
            uid = int(arg)
            if uid not in seen:
                seen.add(uid)
                targets.append({"uid": uid, "username": None, "found": True})
            continue
        if arg.startswith("@"):
            username = arg[1:]
            if not username:
                continue
            try:
                user = await message._client.get_users(username)
                uid = user.id
                if uid not in seen:
                    seen.add(uid)
                    targets.append({"uid": uid, "username": username, "found": True})
            except Exception:
                targets.append({"uid": None, "username": username, "found": False})
            continue

    if targets:
        return targets

    if message.reply_to_message:
        r = message.reply_to_message
        uid = None
        username = None

        if r.from_user:
            uid = r.from_user.id
            username = r.from_user.username
        elif getattr(r, "forward_from", None):
            uid = r.forward_from.id
            username = r.forward_from.username
        elif getattr(r, "sender_chat", None) and getattr(r.sender_chat, "type", None) == "private":
            uid = r.sender_chat.id
            username = getattr(r.sender_chat, "username", None)

        if uid:
            return [{"uid": uid, "username": username, "found": True}]

    return []


async def format_user_label(client, uid, item_template):
    try:
        user = await client.get_users(int(uid))
        name = user.first_name or user.username or str(uid)
    except Exception:
        name = str(uid)
    safe_name = html.escape(name, quote=False)
    return item_template.format(uid=int(uid), label=safe_name)


def get_emoji(message) -> str:
    parts = (message.text or "").split()
    for p in reversed(parts[1:]):
        if not p.lstrip("-").isdigit() and not p.startswith("@"):
            return p
    return "👍"


async def get_available_reactions(client, chat_id):
    reactions = []
    try:
        chat = await client.get_chat(chat_id)
        if getattr(chat, "available_reactions", None):
            for reaction in getattr(chat.available_reactions, "reactions", []) or []:
                emoji = getattr(reaction, "emoji", None) or getattr(reaction, "reaction", None)
                if emoji:
                    reactions.append(emoji)
    except Exception:
        pass

    if reactions:
        return reactions

    try:
        result = await client.invoke(functions.messages.GetAvailableReactions(hash=0))
        for reaction in getattr(result, "reactions", []) or []:
            emoji = getattr(reaction, "reaction", None)
            if emoji:
                reactions.append(emoji)
    except Exception:
        pass

    return reactions


def format_mentions(uids, mention_template, separator):
    return separator.join(
        mention_template.format(uid=uid)
        for uid in sorted(set(int(uid) for uid in uids))
    )


async def render_user_list(client, uids, item_template):
    entries = []
    for uid in sorted(set(int(x) for x in uids)):
        try:
            user = await client.get_users(uid)
            name = user.first_name or user.username or str(uid)
        except Exception:
            name = str(uid)
        safe_name = html.escape(name, quote=False)
        entries.append(item_template.format(uid=uid, label=safe_name))
    return "\n".join(entries)


async def edit_or_reply(
    message,
    text: str,
    parse_mode=None,
    reply_markup=None,
    apply_response_style=True,
):
    if apply_response_style:
        text = format_response(text)
    parse_mode = ParseMode.HTML
    chat_id = message.chat.id
    saved_messages = chat_id == getattr(state, "OWNER_ID", None)
    target_chat = "me" if saved_messages else chat_id
    try:
        await message._client.edit_message_text(
            target_chat, message.id, text, parse_mode=parse_mode, reply_markup=reply_markup
        )
        return True
    except Exception:
        logger.exception("edit_message_text failed for chat=%s message=%s", target_chat, message.id)
        try:
            await message.edit(text, parse_mode=parse_mode, reply_markup=reply_markup)
            return True
        except Exception:
            logger.exception("Message.edit fallback failed for chat=%s message=%s", chat_id, message.id)
            try:
                await message.reply(text, parse_mode=parse_mode, reply_markup=reply_markup)
                return True
            except Exception:
                logger.exception("reply fallback failed for chat=%s message=%s", chat_id, message.id)
                return False
