from pyrogram import filters
from utils.state import state
from config import OWNER_ID as DEFAULT_OWNER_ID


def _owner_check(_, __, message):
    owner_id = state.OWNER_ID if getattr(state, "OWNER_ID", None) is not None else DEFAULT_OWNER_ID
    if owner_id is None:
        return True

    # Saved Messages can arrive without a usable from_user.  The private chat
    # id is the account owner's id, so accept it before checking the sender.
    if message.chat and getattr(message.chat, "id", None) == owner_id:
        return True

    if message.from_user:
        return message.from_user.id == owner_id

    if message.chat and message.chat.type == "private":
        return message.chat.id == owner_id

    sender_chat = getattr(message, "sender_chat", None)
    if sender_chat and getattr(sender_chat, "id", None) == owner_id:
        return True

    return False


owner_only = filters.create(_owner_check)
# Pyrogram documents Saved Messages as incoming (not outgoing). Keep an
# explicit `me` chat filter so user-account commands are never missed there.
owner_command = (filters.outgoing | filters.incoming | filters.chat("me")) & owner_only
