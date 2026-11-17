import logging

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from commands.command_registry import (
    HELP_ENTRY_PATTERN,
    HELP_ENTRYPOINT,
    HELP_BACK_LABEL,
    HELP_CALLBACK_HOME,
    HELP_CALLBACK_PATTERN,
    HELP_CALLBACK_PREFIX,
    HELP_INLINE_QUERY_PREFIX,
    HELP_SECTION_LABELS,
    MSG_HELP_CANNOT_EDIT,
    MSG_HELP_INLINE_DESCRIPTION,
    MSG_HELP_INLINE_TITLE,
    MSG_HELP_SECTION_DESCRIPTION,
    MSG_HELP_SECTION_FAILED_ALERT,
    MSG_HELP_SECTION_NOT_FOUND_ALERT,
    build_help_section_text,
    build_help_text,
    help_section_names,
    resolve_help_section,
)
logger = logging.getLogger(__name__)


def build_help_keyboard(section: str | None = None):
    if section is None:
        sections = help_section_names()
        buttons = [
            InlineKeyboardButton(
                text=HELP_SECTION_LABELS[name],
                callback_data=f"{HELP_CALLBACK_PREFIX}{name}",
            )
            for name in sections
        ]
        rows = [buttons[index:index + 2] for index in range(0, len(buttons), 2)]
        return InlineKeyboardMarkup(rows)

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(HELP_BACK_LABEL, callback_data=HELP_CALLBACK_HOME)]]
    )


def setup_help_bot(app: Client, owner_id: int):
    @app.on_inline_query()
    async def inline_help(_, inline_query):
        if not inline_query.from_user or inline_query.from_user.id != owner_id:
            await app.answer_inline_query(inline_query.id, results=[], cache_time=0, is_personal=True)
            return

        query = " ".join((inline_query.query or "").strip().lower().split())
        if query.startswith(HELP_INLINE_QUERY_PREFIX):
            query = query[len(HELP_INLINE_QUERY_PREFIX):].strip()
        elif query == HELP_ENTRYPOINT:
            query = ""
        section = resolve_help_section(query)
        if section in help_section_names():
            title = HELP_SECTION_LABELS[section]
            text = build_help_section_text(section)
            markup = build_help_keyboard(section)
            description = MSG_HELP_SECTION_DESCRIPTION.format(title=title)
        else:
            title = MSG_HELP_INLINE_TITLE
            text = build_help_text()
            markup = build_help_keyboard()
            description = MSG_HELP_INLINE_DESCRIPTION

        result = InlineQueryResultArticle(
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(
                text, parse_mode=ParseMode.HTML
            ),
            reply_markup=markup,
        )
        await app.answer_inline_query(
            inline_query.id,
            results=[result],
            cache_time=0,
            is_personal=True,
        )

    @app.on_message(filters.private & filters.regex(HELP_ENTRY_PATTERN))
    async def show_help(_, message):
        if not message.from_user or message.from_user.id != owner_id:
            return
        await message.reply_text(
            build_help_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=build_help_keyboard(),
        )

    @app.on_callback_query(filters.regex(HELP_CALLBACK_PATTERN))
    async def handle_help_callback(_, callback_query):
        if not callback_query.from_user or callback_query.from_user.id != owner_id:
            await callback_query.answer()
            return

        section = callback_query.matches[0].group(1)
        if section == "home":
            text = build_help_text()
            markup = build_help_keyboard()
        else:
            canonical_section = resolve_help_section(section)
            if canonical_section not in help_section_names():
                await callback_query.answer(MSG_HELP_SECTION_NOT_FOUND_ALERT, show_alert=True)
                return
            text = build_help_section_text(canonical_section)
            markup = build_help_keyboard(canonical_section)

        try:
            inline_message_id = getattr(callback_query, "inline_message_id", None)
            if inline_message_id:
                await app.edit_inline_text(
                    inline_message_id,
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup,
                )
            elif callback_query.message:
                await callback_query.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup,
                )
            else:
                await callback_query.answer(MSG_HELP_CANNOT_EDIT, show_alert=True)
                return
            await callback_query.answer()
        except Exception as error:
            logger.exception("Help menu callback failed")
            await callback_query.answer(MSG_HELP_SECTION_FAILED_ALERT, show_alert=True)