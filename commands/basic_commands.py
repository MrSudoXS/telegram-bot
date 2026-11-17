import asyncio
import logging
from pyrogram.errors import RPCError

from pyrogram import filters
from utils import state, edit_or_reply, owner_command
from commands.command_registry import (
    build_help_text,
    build_help_section_text,
    CMD_HELP,
    HELP_ENTRYPOINT,
    CMD_STATUS,
    CMD_PING,
    MSG_BASIC_HELP_DISCONNECTED,
    MSG_BASIC_HELP_CONNECTION_DETAIL,
    MSG_BASIC_HELP_TIMEOUT,
    MSG_BASIC_HELP_EMPTY_RESULTS,
    MSG_BASIC_HELP_TELEGRAM_ERROR,
    MSG_BASIC_HELP_OTHER_ERROR,
    MSG_BASIC_HELP_INSERT_FAILED,
    MSG_BASIC_STATUS,
    MSG_BASIC_PING,
)
logger = logging.getLogger(__name__)


def setup_basic_commands(app):
    @app.on_message(owner_command & filters.regex(CMD_HELP))
    async def help_cmd(client, message):
        parts = (message.text or "").strip().split(maxsplit=1)
        section = parts[1] if len(parts) > 1 else ""
        if section:
            await edit_or_reply(
                message,
                build_help_section_text(section),
                apply_response_style=False,
            )
            return

        help_client = state.HELP_BOT_CLIENT
        if help_client is None or not state.HELP_BOT_USERNAME:
            start_error = state.HELP_BOT_START_ERROR
            details = (
                MSG_BASIC_HELP_CONNECTION_DETAIL.format(error=start_error)
                if start_error else ""
            )
            await edit_or_reply(
                message,
                MSG_BASIC_HELP_DISCONNECTED + "\n"
                f"{details}",
            )
            return

        chat = message.chat
        is_saved_messages = chat.id == state.OWNER_ID
        target_chat_id = "me" if is_saved_messages else chat.id
        try:
            inline_results = await client.get_inline_bot_results(
                state.HELP_BOT_USERNAME,
                query=HELP_ENTRYPOINT,
            )
            if not inline_results.results:
                raise RuntimeError("Help bot returned no inline results")

            await client.send_inline_bot_result(
                target_chat_id,
                inline_results.query_id,
                inline_results.results[0].id,
                message_thread_id=getattr(message, "message_thread_id", None),
            )
            try:
                await message.delete()
            except Exception:
                logger.exception("Help inline result sent but command message %s could not be deleted", message.id)
        except Exception as error:
            logger.exception("Could not insert Help inline result into chat %s", target_chat_id)
            if isinstance(error, RPCError):
                reason = MSG_BASIC_HELP_TELEGRAM_ERROR.format(
                    error_type=error.__class__.__name__, error=error
                )
            elif isinstance(error, (TimeoutError, asyncio.TimeoutError)):
                reason = MSG_BASIC_HELP_TIMEOUT
            elif isinstance(error, RuntimeError) and "no inline results" in str(error):
                reason = MSG_BASIC_HELP_EMPTY_RESULTS.format(query=HELP_ENTRYPOINT)
            else:
                reason = MSG_BASIC_HELP_OTHER_ERROR.format(
                    error_type=error.__class__.__name__, error=error
                )

            confirmation = MSG_BASIC_HELP_INSERT_FAILED.format(
                reason=reason,
                username=state.HELP_BOT_USERNAME,
            )
            await edit_or_reply(message, confirmation)

    @app.on_message(owner_command & filters.regex(CMD_STATUS))
    async def status_cmd(client, message):
        text = MSG_BASIC_STATUS.format(
            enemies=len(state.ENEMIES),
            spams=len(state.SPAMS),
            auto_spams=len(state.AUTO_SPAMS),
            muted=len(state.MUTED),
            reactions=len(state.REACTIONS),
        )
        await edit_or_reply(message, text)

    @app.on_message(owner_command & filters.regex(CMD_PING))
    async def ping_cmd(client, message):
        await edit_or_reply(message, MSG_BASIC_PING)
