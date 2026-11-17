from pyrogram import filters
from utils import owner_command, state, get_user_info, edit_or_reply
from commands.command_registry import (
    CMD_MUTE,
    CMD_REMOVE_MUTE,
    CMD_LIST_MUTE,
    CMD_CLEAR_MUTE,
    MSG_USAGE_MUTE,
    MSG_USAGE_REMOVE_MUTE,
    MSG_MUTED_ADDED,
    MSG_MUTED_REMOVED,
    MSG_LIST_MUTED_EMPTY,
    MSG_MUTED_CLEARED,
    MSG_MUTE_LIST_TITLE,
    MSG_LIST_UID_ITEM,
)


def setup_mute_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_MUTE))
    async def mute_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_MUTE)
            return
        state.add_muted(info["uid"])
        await edit_or_reply(message, MSG_MUTED_ADDED.format(uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_MUTE))
    async def remove_mute(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_REMOVE_MUTE)
            return
        state.remove_muted(info["uid"])
        await edit_or_reply(message, MSG_MUTED_REMOVED.format(uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_LIST_MUTE))
    async def list_muted(client, message):
        if not state.MUTED:
            await edit_or_reply(message, MSG_LIST_MUTED_EMPTY)
            return
        text = MSG_MUTE_LIST_TITLE + "\n".join(
            MSG_LIST_UID_ITEM.format(uid=uid) for uid in sorted(state.MUTED)
        )
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_MUTE))
    async def clear_muted(client, message):
        state.clear_muted()
        await edit_or_reply(message, MSG_MUTED_CLEARED)
