from html import escape
from pyrogram import filters
from utils import owner_command, state, get_user_info, get_emoji, get_available_reactions, edit_or_reply, stylish_time, iran_time, strip_time_suffix
from commands.command_registry import (
    CMD_REACTION,
    CMD_REMOVE_REACTION,
    CMD_LIST_REACTION,
    CMD_CLEAR_REACTION,
    CMD_AVAILABLE_REACTIONS,
    CMD_SET_TIME,
    CMD_DEL_TIME,
    MSG_USAGE_REACTION,
    MSG_USAGE_REMOVE_REACTION,
    MSG_REACTION_SET,
    MSG_REACTION_REMOVED,
    MSG_REACTION_CLEARED,
    MSG_AVAILABLE_REACTIONS_EMPTY,
    MSG_SET_TIME,
    MSG_DEL_TIME,
    MSG_REACTION_INVALID,
    MSG_LIST_REACTIONS_EMPTY,
    MSG_REACTIONS_LIST_TITLE,
    MSG_REACTION_LIST_ITEM,
    MSG_AVAILABLE_REACTIONS_TITLE,
)


def setup_reaction_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_REACTION))
    async def reaction_cmd(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_REACTION)
            return
        emoji = get_emoji(message).strip()
        if not emoji:
            await edit_or_reply(message, MSG_REACTION_INVALID)
            return
        available = await get_available_reactions(client, message.chat.id)
        # don't block valid emoji just because the chat list is limited
        state.set_reaction(info["uid"], emoji)
        await edit_or_reply(message, MSG_REACTION_SET.format(emoji=emoji, uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_REMOVE_REACTION))
    async def remove_reaction(client, message):
        info = await get_user_info(message)
        if not info["found"] or not info["uid"]:
            await edit_or_reply(message, MSG_USAGE_REMOVE_REACTION)
            return
        state.remove_reaction(info["uid"])
        await edit_or_reply(message, MSG_REACTION_REMOVED.format(uid=info["uid"]))

    @app.on_message(owner_command & filters.regex(CMD_LIST_REACTION))
    async def list_reactions(client, message):
        if not state.REACTIONS:
            await edit_or_reply(message, MSG_LIST_REACTIONS_EMPTY)
            return

        rows = []
        for uid, emoji in sorted(state.REACTIONS.items(), key=lambda item: int(item[0])):
            try:
                user = await client.get_users(int(uid))
                name = " ".join(
                    part for part in (user.first_name, user.last_name) if part
                ) or user.username or str(uid)
                label = f'<a href="tg://user?id={int(uid)}">{escape(name)}</a>'
            except Exception:
                label = escape(str(uid))
            rows.append(
                MSG_REACTION_LIST_ITEM.format(user=label, emoji=escape(str(emoji)))
            )

        await edit_or_reply(message, MSG_REACTIONS_LIST_TITLE + "\n".join(rows))

    @app.on_message(owner_command & filters.regex(CMD_CLEAR_REACTION))
    async def clear_reactions(client, message):
        state.clear_reactions()
        await edit_or_reply(message, MSG_REACTION_CLEARED)

    @app.on_message(owner_command & filters.regex(CMD_AVAILABLE_REACTIONS))
    async def available_reactions_cmd(client, message):
        available = await get_available_reactions(client, message.chat.id)
        if not available:
            await edit_or_reply(message, MSG_AVAILABLE_REACTIONS_EMPTY)
            return
        text = MSG_AVAILABLE_REACTIONS_TITLE + " ".join(available[:50])
        await edit_or_reply(message, text)


def setup_time_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_SET_TIME))
    async def set_timename(client, message):
        state.set_time_name(True)
        if state.BASE_NAME:
            base_name = strip_time_suffix(state.BASE_NAME)
            try:
                await client.update_profile(first_name=f"{base_name} {stylish_time(iran_time())}")
            except Exception:
                pass
        await edit_or_reply(message, MSG_SET_TIME)

    @app.on_message(owner_command & filters.regex(CMD_DEL_TIME))
    async def del_timename(client, message):
        state.set_time_name(False)
        if state.BASE_NAME:
            base_name = strip_time_suffix(state.BASE_NAME)
            try:
                await client.update_profile(first_name=base_name)
            except Exception:
                pass
        await edit_or_reply(message, MSG_DEL_TIME)
