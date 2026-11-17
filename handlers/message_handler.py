import asyncio
import html
import logging
import random
from datetime import datetime, timedelta, timezone
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.raw import functions, types as raw_types
from config import RATE_LIMIT_DELAY, MESSAGES_PER_BATCH, AUTO_SPAM_INTERVAL
from utils import state, stylish_time, iran_time, strip_time_suffix
from commands.command_registry import COMMAND_SKIP_PREFIXES, MSG_USER_MENTION_LINK

logger = logging.getLogger(__name__)


async def _spam_messages(client, chat_id, reply_to, count):
    for _ in range(count):
        try:
            await client.send_message(
                chat_id,
                random.choice(state.REPLIES),
                reply_to_message_id=reply_to,
            )
            await asyncio.sleep(RATE_LIMIT_DELAY)
        except Exception:
            await asyncio.sleep(1)


async def auto_spam_task(client, chat_id, user_id):
    while user_id in state.AUTO_SPAMS:
        try:
            reply_to = state.AUTO_TARGETS.get(user_id)
            await client.send_message(
                chat_id,
                random.choice(state.REPLIES),
                reply_to_message_id=reply_to,
            )
        except Exception as e:
            print(f"[autospam] {e}")
        await asyncio.sleep(AUTO_SPAM_INTERVAL)


async def auto_mention_spam_task(client, chat_id):
    while state.AUTO_MENTION_SPAMS:
        try:
            reply_to = state.AUTO_MENTION_TARGET
            mentions = [
                MSG_USER_MENTION_LINK.format(uid=uid)
                for uid in sorted(state.AUTO_MENTION_SPAMS)
            ]
            if not mentions:
                break
            reply_text = html.escape(random.choice(state.REPLIES))
            text = reply_text + "\n" + "  ,  ".join(mentions)
            await client.send_message(
                chat_id,
                text,
                reply_to_message_id=reply_to,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            print(f"[auto_mention_spam] {e}")
        await asyncio.sleep(AUTO_SPAM_INTERVAL)


async def _apply_reaction(client, message, emoji):
    """Use compatible Pyrogram paths because Telegram varies by chat type."""
    async def send_raw_reaction():
        peer = await client.resolve_peer(message.chat.id)
        request = functions.messages.SendReaction(
            peer=peer,
            msg_id=message.id,
            reaction=[raw_types.ReactionEmoji(emoticon=emoji)],
            big=False,
            add_to_recent=True,
        )
        await client.invoke(request)

    attempts = [
        lambda: client.send_reaction(
            message.chat.id, message_id=message.id, emoji=emoji, add_to_recent=True
        ),
        lambda: client.send_reaction(message.chat.id, message.id, emoji),
        send_raw_reaction,
        lambda: message.react(emoji=emoji),
    ]
    last_error = None
    for attempt in attempts:
        try:
            await attempt()
            return True
        except Exception as error:
            last_error = error
    logger.error(
        "Reaction failed: %s chat=%s message=%s",
        last_error,
        message.chat.id,
        message.id,
    )
    return False


async def _send_enemy_reply(client, message, text):
    payload = text
    try:
        await client.send_message(
            message.chat.id,
            payload,
            reply_to_message_id=message.id,
        )
        return True
    except Exception as error:
        try:
            await client.send_message(
                message.chat.id,
                payload,
                reply_to_message_id=message.id,
            )
            return True
        except Exception as fallback_error:
            logger.error("Enemy reply failed: %s; fallback failed: %s", error, fallback_error)
            return False


async def time_name_task(client):
    while True:
        if state.TIME_NAME and state.BASE_NAME:
            t = stylish_time(iran_time())
            base_name = strip_time_suffix(state.BASE_NAME)
            try:
                await client.update_profile(first_name=f"{base_name} {t}")
            except Exception:
                pass
        now = datetime.now(timezone(timedelta(hours=3, minutes=30)))
        sleep_seconds = 60 - now.second
        if sleep_seconds <= 0:
            sleep_seconds = 60
        await asyncio.sleep(sleep_seconds)


def setup_message_handler(app):
    # Saved Messages are exposed by Pyrogram as incoming updates. Exclude
    # that chat here so this catch-all handler cannot consume commands before
    # the actual command handlers get a chance to process them.
    @app.on_message(filters.incoming & ~filters.bot & ~filters.chat("me"), group=1)
    async def handle_message(client, message):
        try:
            if not message.from_user:
                return

            text = message.text or ""
            if text.startswith(COMMAND_SKIP_PREFIXES):
                return

            sender_id = message.from_user.id
            chat_id   = message.chat.id
            msg_id    = message.id

            if sender_id in state.MUTED:
                if sender_id in state.ENEMIES:
                    await asyncio.sleep(RATE_LIMIT_DELAY)
                    try:
                        await _send_enemy_reply(
                            client, message,
                            state.ENEMY_RESPONSES.get(str(sender_id)) or random.choice(state.REPLIES),
                        )
                    except Exception as e:
                        print(f"[enemy reply muted] {e}")

                if sender_id in state.SPAMS:
                    asyncio.create_task(_spam_messages(client, chat_id, msg_id, MESSAGES_PER_BATCH))

                if str(sender_id) in state.REACTIONS:
                    await _apply_reaction(client, message, str(state.REACTIONS[str(sender_id)]).strip())

                try:
                    await message.delete()
                except Exception:
                    pass
                return

            if sender_id in state.ENEMIES:
                await asyncio.sleep(RATE_LIMIT_DELAY)
                try:
                    await _send_enemy_reply(
                        client, message,
                        state.ENEMY_RESPONSES.get(str(sender_id)) or random.choice(state.REPLIES),
                    )
                except Exception as e:
                    print(f"[enemy reply] {e}")

            if sender_id in state.SPAMS:
                asyncio.create_task(_spam_messages(client, chat_id, msg_id, MESSAGES_PER_BATCH))

            if str(sender_id) in state.REACTIONS:
                emoji = str(state.REACTIONS[str(sender_id)]).strip()
                if emoji:
                    await _apply_reaction(client, message, emoji)

        except Exception as e:
            print(f"[handler] {e}")
