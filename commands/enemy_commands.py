from html import escape
from pyrogram import filters
from utils import owner_command, state, get_user_info, edit_or_reply
from commands.command_registry import (
    CMD_ENEMY,
    CMD_REMOVE_ENEMY,
    CMD_LIST_ENEMY,
    CMD_CLEAR_ENEMY,
    MSG_USAGE_ENEMY,
    MSG_USAGE_REMOVE_ENEMY,
    MSG_LIST_ENEMY_EMPTY,
    MSG_ENEMY_CLEARED,
    MSG_ENEMY_RANDOM_RESPONSE,
    MSG_ENEMY_KIND_CUSTOM,
    MSG_ENEMY_KIND_RANDOM,
    MSG_ENEMY_ADDED_CONFIRMATION,
    MSG_ENEMY_REMOVED_CONFIRMATION,
    MSG_ENEMY_LIST_TITLE,
    MSG_ENEMY_LIST_ITEM,
    MSG_ENEMY_LIST_RESPONSE,
)


def setup_enemy_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_ENEMY))
    async def enemy_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_ENEMY)
            return
        raw = (message.text or "").strip()
        parts = raw.split(maxsplit=1)
        response = parts[1].strip() if len(parts) > 1 else None
        if not message.reply_to_message and response:
            first, *rest = response.split(maxsplit=1)
            if first.lstrip("-").isdigit() or first.startswith("@"):
                response = rest[0] if rest else None
        state.add_enemy(info["uid"], response)
        try:
            user = await client.get_users(info["uid"])
            name = " ".join(x for x in [user.first_name, user.last_name] if x) or user.username
        except Exception:
            name = None
        name = name or info.get("display_name") or info.get("username") or str(info["uid"])
        label = f'<a href="tg://user?id={int(info["uid"])}">{escape(name)}</a>'
        selected = escape(response) if response else MSG_ENEMY_RANDOM_RESPONSE
        kind = MSG_ENEMY_KIND_CUSTOM if response else MSG_ENEMY_KIND_RANDOM
        confirmation = MSG_ENEMY_ADDED_CONFIRMATION.format(
            label=label, kind=kind, response=selected
        )
        await edit_or_reply(message, confirmation)

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_ENEMY))
    async def remove_enemy(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_REMOVE_ENEMY)
            return
        state.remove_enemy(info["uid"])
        try:
            user = await client.get_users(info["uid"])
            name = " ".join(x for x in [user.first_name, user.last_name] if x) or user.username
        except Exception:
            name = None
        name = name or info.get("display_name") or info.get("username") or str(info["uid"])
        label = f'<a href="tg://user?id={int(info["uid"])}">{escape(name)}</a>'
        confirmation = MSG_ENEMY_REMOVED_CONFIRMATION.format(label=label)
        await edit_or_reply(message, confirmation)

    @app.on_message(owner_command & filters.regex(CMD_LIST_ENEMY))
    async def list_enemies(client, message):
        if not state.ENEMIES:
            await edit_or_reply(message, MSG_LIST_ENEMY_EMPTY)
            return
        labels = []
        for uid in sorted(state.ENEMIES):
            try:
                user = await client.get_users(uid)
                name = " ".join(x for x in [user.first_name, user.last_name] if x) or user.username or str(uid)
            except Exception:
                name = str(uid)
            label = f'<a href="tg://user?id={int(uid)}">{escape(name)}</a>'
            response = state.ENEMY_RESPONSES.get(str(uid)) or ""
            kind = MSG_ENEMY_KIND_CUSTOM if response else MSG_ENEMY_KIND_RANDOM
            response_text = MSG_ENEMY_LIST_RESPONSE.format(response=escape(response)) if response else ""
            labels.append(MSG_ENEMY_LIST_ITEM.format(label=label, kind=kind, response_text=response_text))
        text = MSG_ENEMY_LIST_TITLE + "\n" + "\n".join(labels)
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_ENEMY))
    async def clear_enemies(client, message):
        state.clear_enemies()
        await edit_or_reply(message, MSG_ENEMY_CLEARED)
