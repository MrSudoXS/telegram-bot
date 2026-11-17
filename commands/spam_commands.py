import asyncio
from pyrogram import filters
from config import RATE_LIMIT_DELAY
from utils import owner_command, state, get_user_info, edit_or_reply
from commands.command_registry import (
    CMD_SPAM,
    CMD_REMOVE_SPAM,
    CMD_LIST_SPAM,
    CMD_CLEAR_SPAM,
    MSG_USAGE_SPAM,
    MSG_USAGE_REMOVE_SPAM,
    MSG_SPAM_REMOVED,
    MSG_LIST_SPAM_EMPTY,
    MSG_SPAM_CLEARED,
    MSG_SPAM_IN_PROGRESS,
    MSG_SPAM_LIST_TITLE,
    MSG_LIST_UID_ITEM,
)

MAX_SPAM_COUNT = 200


def _parse_spam_command(message):
    text = (message.text or "").strip()
    parts = text.split()
    if len(parts) < 3:
        return None

    count_token = parts[-1]
    if not count_token.isdigit():
        return None

    count = int(count_token)
    if count < 1:
        return None

    if message.reply_to_message:
        spam_text = " ".join(parts[1:-1]).strip()
    else:
        if len(parts) == 3:
            spam_text = parts[1].strip()
        else:
            spam_text = " ".join(parts[1:-1]).strip()

    if not spam_text:
        return None

    return count, spam_text


async def _send_spam_messages(client, chat_id, text, count, reply_to=None):
    for i in range(count):
        try:
            await client.send_message(
                chat_id,
                text,
                reply_to_message_id=reply_to,
            )
        except Exception as e:
            print(f"[spam_cmd] {e}")
            await asyncio.sleep(RATE_LIMIT_DELAY * 2)
        else:
            if (i + 1) % 10 == 0:
                await asyncio.sleep(RATE_LIMIT_DELAY + 1)
            else:
                await asyncio.sleep(RATE_LIMIT_DELAY)


def setup_spam_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_SPAM))
    async def spam_cmd(client, message):
        parse_result = _parse_spam_command(message)
        if parse_result is None:
            await edit_or_reply(message, MSG_USAGE_SPAM)
            return

        count, spam_text = parse_result
        info = await get_user_info(message)

        if count > MAX_SPAM_COUNT:
            count = MAX_SPAM_COUNT

        reply_to = None

        if message.reply_to_message:
            reply_to = message.reply_to_message.id
        elif info["found"] and info["uid"]:
            mention = f"@{info['username']}" if info.get("username") else str(info["uid"])
            spam_text = f"{spam_text}\n{mention}"

        asyncio.create_task(
            _send_spam_messages(
                client,
                message.chat.id,
                spam_text,
                count,
                reply_to=reply_to,
            )
        )
        await edit_or_reply(message, MSG_SPAM_IN_PROGRESS.format(count=count))

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_SPAM))
    async def remove_spam(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_REMOVE_SPAM)
            return
        state.remove_spam(info["uid"])
        await edit_or_reply(message, MSG_SPAM_REMOVED.format(uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_LIST_SPAM))
    async def list_spams(client, message):
        if not state.SPAMS:
            await edit_or_reply(message, MSG_LIST_SPAM_EMPTY)
            return
        text = MSG_SPAM_LIST_TITLE + "\n".join(
            MSG_LIST_UID_ITEM.format(uid=uid) for uid in sorted(state.SPAMS)
        )
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_SPAM))
    async def clear_spams(client, message):
        state.clear_spams()
        await edit_or_reply(message, MSG_SPAM_CLEARED)
