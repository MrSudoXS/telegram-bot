from pyrogram import filters
from pyrogram.enums import ParseMode
from utils import owner_command, get_user_info, edit_or_reply
from commands.command_registry import (
    CMD_ID,
    CMD_USERID,
    MSG_ID_USAGE,
    MSG_ID_INFO,
)


def setup_id_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_ID))
    async def id_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_ID_USAGE, parse_mode=ParseMode.HTML)
            return

        try:
            user = await client.get_users(info["uid"])
            user_name = user.first_name or user.username or str(info["uid"])
        except Exception:
            user_name = info.get("username") or str(info["uid"])

        text = MSG_ID_INFO.format(uid=info["uid"], name=user_name)
        await edit_or_reply(message, text, parse_mode=ParseMode.HTML)

    @app.on_message(owner_command & filters.regex(CMD_USERID))
    async def userid_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_ID_USAGE, parse_mode=ParseMode.HTML)
            return

        try:
            user = await client.get_users(info["uid"])
            user_name = user.first_name or user.username or str(info["uid"])
        except Exception:
            user_name = info.get("username") or str(info["uid"])

        text = MSG_ID_INFO.format(uid=info["uid"], name=user_name)
        await edit_or_reply(message, text, parse_mode=ParseMode.HTML)
