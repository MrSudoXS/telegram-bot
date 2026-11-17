import asyncio
from pyrogram import filters
from utils import owner_command, state, get_user_info, parse_user_targets, format_mentions, render_user_list, edit_or_reply
from handlers.message_handler import auto_spam_task, auto_mention_spam_task
from commands.command_registry import (
    CMD_AUTOSPAM,
    CMD_AUTOSPAM_MENTION,
    CMD_REMOVE_AUTOSPAM,
    CMD_REMOVE_AUTOSPAM_MENTION,
    CMD_LIST_AUTOSPAM,
    CMD_LIST_AUTOSPAM_MENTION,
    CMD_CLEAR_AUTOSPAM,
    CMD_CLEAR_AUTOSPAM_MENTION,
    MSG_USAGE_AUTOSPAM,
    MSG_USAGE_AUTOSPAM_MENTION,
    MSG_AUTOSPAM_ALREADY_RUNNING,
    MSG_AUTOSPAM_STARTED,
    MSG_AUTOSPAM_STOPPED,
    MSG_LIST_AUTOSPAM_EMPTY,
    MSG_AUTOSPAM_CLEARED,
    MSG_AUTOSPAM_MENTION_STARTED,
    MSG_AUTOSPAM_MENTION_NOT_FOUND,
    MSG_AUTOSPAM_MENTION_REMOVED,
    MSG_LIST_AUTOSPAM_MENTION_EMPTY,
    MSG_AUTOSPAM_MENTION_CLEARED,
    MSG_AUTOSPAM_MENTION_NO_ACTIVE,
    MSG_AUTOSPAM_LIST_TITLE,
    MSG_AUTOSPAM_MENTION_LIST_TITLE,
    MSG_USER_LIST_ITEM,
    MSG_USER_MENTION_LINK,
    MSG_MENTIONS_SEPARATOR,
    MSG_LIST_UID_ITEM,
)


def setup_autospam_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_AUTOSPAM))
    async def autospam_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_AUTOSPAM)
            return
        uid = info["uid"]
        target_msg_id = message.reply_to_message.id if message.reply_to_message else None
        if uid in state.AUTO_SPAMS:
            if target_msg_id is not None:
                state.AUTO_TARGETS[uid] = target_msg_id
            await edit_or_reply(message, MSG_AUTOSPAM_ALREADY_RUNNING)
            return
        state.add_auto_spam(uid)
        state.AUTO_TARGETS[uid] = target_msg_id
        task = asyncio.create_task(auto_spam_task(client, message.chat.id, uid))
        state.AUTO_TASKS[uid] = task
        await edit_or_reply(message, MSG_AUTOSPAM_STARTED.format(uid=uid))

    @app.on_message(owner_command & filters.regex(CMD_AUTOSPAM_MENTION))
    async def autospam_mention_cmd(client, message):
        targets = await parse_user_targets(message)
        if not targets:
            await edit_or_reply(message, MSG_USAGE_AUTOSPAM_MENTION)
            return
        target_ids = [t["uid"] for t in targets if t["found"] and t["uid"]]
        if not target_ids:
            await edit_or_reply(message, MSG_AUTOSPAM_MENTION_NOT_FOUND)
            return
        target_msg_id = message.reply_to_message.id if message.reply_to_message else None
        if target_msg_id is not None:
            state.AUTO_MENTION_TARGET = target_msg_id
        for uid in target_ids:
            state.add_auto_mention_spam(uid)
        if state.AUTO_MENTION_TASK is None:
            state.AUTO_MENTION_TASK = asyncio.create_task(
                auto_mention_spam_task(client, message.chat.id)
            )
        await edit_or_reply(
            message,
            MSG_AUTOSPAM_MENTION_STARTED.format(
                mentions=format_mentions(target_ids, MSG_USER_MENTION_LINK, MSG_MENTIONS_SEPARATOR)
            ),
        )

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_AUTOSPAM))
    async def remove_autospam(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_AUTOSPAM)
            return
        state.remove_auto_spam(info["uid"])
        await edit_or_reply(message, MSG_AUTOSPAM_STOPPED.format(uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_AUTOSPAM_MENTION))
    async def remove_autospam_mention(client, message):
        targets = await parse_user_targets(message)
        if not targets:
            await edit_or_reply(message, MSG_USAGE_AUTOSPAM_MENTION)
            return
        removed = []
        for t in targets:
            if t["found"] and t["uid"] in state.AUTO_MENTION_SPAMS:
                state.remove_auto_mention_spam(t["uid"])
                removed.append(t["uid"])
        if not removed:
            await edit_or_reply(message, MSG_AUTOSPAM_MENTION_NO_ACTIVE)
            return
        await edit_or_reply(
            message,
            MSG_AUTOSPAM_MENTION_REMOVED.format(
                mentions=format_mentions(removed, MSG_USER_MENTION_LINK, MSG_MENTIONS_SEPARATOR)
            ),
        )

    @app.on_message(owner_command & filters.regex(CMD_LIST_AUTOSPAM))
    async def list_autospams(client, message):
        if not state.AUTO_SPAMS:
            await edit_or_reply(message, MSG_LIST_AUTOSPAM_EMPTY)
            return
        text = MSG_AUTOSPAM_LIST_TITLE + "\n".join(
            MSG_LIST_UID_ITEM.format(uid=uid) for uid in sorted(state.AUTO_SPAMS)
        )
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_LIST_AUTOSPAM_MENTION))
    async def list_auto_mention_spams(client, message):
        if not state.AUTO_MENTION_SPAMS:
            await edit_or_reply(message, MSG_LIST_AUTOSPAM_MENTION_EMPTY)
            return
        text = MSG_AUTOSPAM_MENTION_LIST_TITLE + await render_user_list(
            client, state.AUTO_MENTION_SPAMS, MSG_USER_LIST_ITEM
        )
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_AUTOSPAM))
    async def clear_autospams(client, message):
        state.clear_auto_spams()
        await edit_or_reply(message, MSG_AUTOSPAM_CLEARED)

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_AUTOSPAM_MENTION))
    async def clear_autospam_mentions(client, message):
        state.clear_auto_mention_spams()
        await edit_or_reply(message, MSG_AUTOSPAM_MENTION_CLEARED)
