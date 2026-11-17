import asyncio
import ast
import os
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.parser.html import HTML
from pyrogram.types import Chat, InlineKeyboardMarkup, InlineQueryResultArticle, Message, User

import main
from commands import setup_all_commands
from commands import command_registry
from commands.basic_commands import setup_basic_commands
from handlers import setup_message_handler
from handlers.help_bot import build_help_keyboard, setup_help_bot
from handlers.message_handler import _apply_reaction
from commands.reaction_time_commands import setup_reaction_commands
from utils import state
from utils.database import Database
from utils.helpers import edit_or_reply, format_mentions, format_response


COMMAND_EXAMPLES = {
    "CMD_HELP": ".راهنما",
    "CMD_STATUS": ".لیست کلی",
    "CMD_PING": ".پینگ",
    "CMD_ENEMY": ".انمی",
    "CMD_REMOVE_ENEMY": ".حذف انمی @user",
    "CMD_LIST_ENEMY": ".لیست انمی",
    "CMD_CLEAR_ENEMY": ".پاکسازی انمی",
    "CMD_SPAM": ".اسپم متن 2",
    "CMD_REMOVE_SPAM": ".حذف اسپم 123",
    "CMD_LIST_SPAM": ".لیست اسپم",
    "CMD_CLEAR_SPAM": ".پاکسازی اسپم",
    "CMD_AUTOSPAM": ".اتو اسپم @user",
    "CMD_REMOVE_AUTOSPAM": ".حذف اتو 123",
    "CMD_LIST_AUTOSPAM": ".لیست اتو",
    "CMD_CLEAR_AUTOSPAM": ".پاکسازی اتو",
    "CMD_AUTOSPAM_MENTION": ".اتو اسپم منشن @user",
    "CMD_REMOVE_AUTOSPAM_MENTION": ".حذف اتو منشن @user",
    "CMD_LIST_AUTOSPAM_MENTION": ".لیست اتو منشن",
    "CMD_CLEAR_AUTOSPAM_MENTION": ".پاکسازی اتو منشن",
    "CMD_MUTE": ".میوت 123",
    "CMD_REMOVE_MUTE": ".حذف میوت @user",
    "CMD_LIST_MUTE": ".لیست میوت",
    "CMD_CLEAR_MUTE": ".پاکسازی میوت",
    "CMD_REACTION": ".ریاکشن 123 👍",
    "CMD_REMOVE_REACTION": ".حذف ریاکشن @user",
    "CMD_LIST_REACTION": ".لیست ریاکشن",
    "CMD_CLEAR_REACTION": ".پاکسازی ریاکشن",
    "CMD_AVAILABLE_REACTIONS": ".ریاکشن های موجود",
    "CMD_SAVE": ".سیو https://t.me/group/12",
    "CMD_ID": ".ایدی @user",
    "CMD_USERID": ".آیدی 123",
    "CMD_SET_TIME": ".تنظیم ساعت",
    "CMD_DEL_TIME": ".حذف ساعت",
}

LEGACY_COMMANDS = {
    "CMD_HELP": "help",
    "CMD_STATUS": "status",
    "CMD_PING": "ping",
    "CMD_ENEMY": "enemy",
    "CMD_REMOVE_ENEMY": "delete enemy @user",
    "CMD_LIST_ENEMY": "list enemy",
    "CMD_CLEAR_ENEMY": "clear enemy",
    "CMD_SPAM": "spam text 2",
    "CMD_REMOVE_SPAM": "delete spam 123",
    "CMD_LIST_SPAM": "list spam",
    "CMD_CLEAR_SPAM": "clear spam",
    "CMD_AUTOSPAM": "autospam @user",
    "CMD_REMOVE_AUTOSPAM": "delete autospam 123",
    "CMD_LIST_AUTOSPAM": "list autospam",
    "CMD_CLEAR_AUTOSPAM": "clear autospam",
    "CMD_AUTOSPAM_MENTION": "autospam mention @user",
    "CMD_REMOVE_AUTOSPAM_MENTION": "delete autospam mention @user",
    "CMD_LIST_AUTOSPAM_MENTION": "list autospammention",
    "CMD_CLEAR_AUTOSPAM_MENTION": "clear autospam mention",
    "CMD_MUTE": "mute 123",
    "CMD_REMOVE_MUTE": "delete mute @user",
    "CMD_LIST_MUTE": "list mute",
    "CMD_CLEAR_MUTE": "clear mute",
    "CMD_REACTION": "reaction 123 👍",
    "CMD_REMOVE_REACTION": "delete reaction @user",
    "CMD_LIST_REACTION": "list reaction",
    "CMD_CLEAR_REACTION": "clear reaction",
    "CMD_AVAILABLE_REACTIONS": "available reactions",
    "CMD_SAVE": "save https://t.me/group/12",
    "CMD_ID": "id @user",
    "CMD_USERID": "userid 123",
    "CMD_SET_TIME": "settimename",
    "CMD_DEL_TIME": "deltimename",
}


class FakeApp:
    def __init__(self):
        self.handlers = []
        self.inline_handlers = []

    def on_message(self, filters, group=0):
        def register(callback):
            self.handlers.append((callback, filters, group))
            return callback

        return register

    def on_callback_query(self, filters, group=0):
        def register(callback):
            self.callback_handlers.append((callback, filters, group))
            return callback

        if not hasattr(self, "callback_handlers"):
            self.callback_handlers = []
        return register

    def on_inline_query(self, filters=None, group=0):
        def register(callback):
            self.inline_handlers.append((callback, filters, group))
            return callback

        return register


class ContractTests(unittest.IsolatedAsyncioTestCase):
    def test_command_patterns_compile_and_match(self):
        for name, example in COMMAND_EXAMPLES.items():
            with self.subTest(command=name):
                pattern = getattr(command_registry, name)
                self.assertIsNotNone(re.compile(pattern))
                self.assertRegex(example, pattern)
        self.assertNotRegex(".ریاکشن های موجود", command_registry.CMD_REACTION)

    def test_commands_require_dot_and_reject_english_aliases(self):
        for name, old_example in LEGACY_COMMANDS.items():
            pattern = getattr(command_registry, name)
            with self.subTest(command=name, example=old_example):
                self.assertNotRegex(old_example, pattern)
                self.assertNotRegex(f".{old_example}", pattern)
                self.assertNotRegex(f"/{COMMAND_EXAMPLES[name]}", pattern)
                self.assertNotRegex(COMMAND_EXAMPLES[name][1:], pattern)
                self.assertTrue(
                    any(COMMAND_EXAMPLES[name].startswith(prefix)
                        for prefix in command_registry.COMMAND_SKIP_PREFIXES)
                )

    def test_all_command_patterns_are_in_the_contract_map(self):
        command_patterns = [
            name for name, value in vars(command_registry).items()
            if name.startswith("CMD_") and isinstance(value, str)
        ]
        self.assertEqual(set(command_patterns), set(COMMAND_EXAMPLES))

    def test_command_handlers_precede_general_message_handler(self):
        app = FakeApp()
        setup_message_handler(app)
        setup_all_commands(app)
        general_handlers = [entry for entry in app.handlers if entry[0].__name__ == "handle_message"]
        self.assertEqual(len(general_handlers), 1)
        self.assertEqual(general_handlers[0][2], 1)
        self.assertTrue(any(callback.__name__ == "help_cmd" and group == 0
                            for callback, _, group in app.handlers))
        self.assertFalse(any(callback.__name__ == "help_callback" for callback, _, _ in app.handlers))

    async def test_registered_commands_accept_saved_messages(self):
        app = FakeApp()
        app.loop = asyncio.get_running_loop()
        app.executor = None
        setup_message_handler(app)
        setup_all_commands(app)
        saved_chat_id = 987654321
        previous_owner_id = state.OWNER_ID
        state.OWNER_ID = saved_chat_id
        try:
            for command_name, example in COMMAND_EXAMPLES.items():
                saved_chat_message = Message(
                    client=app,
                    id=1,
                    chat=Chat(id=saved_chat_id, type=ChatType.PRIVATE),
                    from_user=User(id=saved_chat_id, is_self=True, is_bot=False),
                    text=example,
                    outgoing=False,
                )
                matching_handlers = []
                for callback, handler_filter, group in app.handlers:
                    if group == 0 and callback.__name__ != "handle_message":
                        if await handler_filter(app, saved_chat_message):
                            matching_handlers.append(callback.__name__)
                with self.subTest(command=command_name):
                    self.assertTrue(matching_handlers, f"No Saved Messages handler matched {example!r}")
        finally:
            state.OWNER_ID = previous_owner_id

    async def test_saved_message_response_edits_me_message(self):
        owner_id = state.OWNER_ID

        class Client:
            async def edit_message_text(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        client = Client()
        message = SimpleNamespace(
            chat=SimpleNamespace(id=987654321),
            id=42,
            _client=client,
            edit=None,
            reply=None,
            delete=None,
        )
        state.OWNER_ID = 987654321
        try:
            self.assertTrue(await edit_or_reply(message, "A < B & C > D"))
        finally:
            state.OWNER_ID = owner_id
        self.assertEqual(client.args[:2], ("me", 42))
        self.assertIs(client.kwargs["parse_mode"], ParseMode.HTML)
        self.assertIn("A &lt; B &amp; C &gt; D", client.args[2])
        self.assertNotIn("<blockquote>", client.args[2])
        self.assertIn("- ᴾˢʸᶜʰᵒ", client.args[2])
        self.assertNotIn("-Void", client.args[2])

    async def test_short_feedback_stays_direct_without_quote(self):
        parsed = await HTML(None).parse(format_response("پیام ذخیره شد."))
        entity_types = {type(entity).__name__ for entity in parsed["entities"]}
        self.assertNotIn("MessageEntityBlockquote", entity_types)
        self.assertIn("MessageEntityBold", entity_types)
        self.assertIn("- ᴾˢʸᶜʰᵒ", parsed["message"])

    async def test_edit_or_reply_can_send_manually_styled_text_without_signature(self):
        class Client:
            async def edit_message_text(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        client = Client()
        message = SimpleNamespace(
            chat=SimpleNamespace(id=123),
            id=5,
            _client=client,
            edit=None,
            reply=None,
        )
        self.assertTrue(
            await edit_or_reply(
                message,
                "<b>راهنمای دستی</b>\n<code>.انمی</code>",
                apply_response_style=False,
            )
        )
        self.assertEqual(client.args[2], "<b>راهنمای دستی</b>\n<code>.انمی</code>")
        self.assertNotIn("<blockquote>", client.args[2])
        self.assertNotIn("-Void", client.args[2])

    async def test_response_format_becomes_quote_and_bold_entities(self):
        parsed = await HTML(None).parse(format_response("Title\nA < B & C > D"))
        entity_types = {type(entity).__name__ for entity in parsed["entities"]}
        self.assertIn("MessageEntityBlockquote", entity_types)
        self.assertIn("MessageEntityBold", entity_types)
        self.assertIn("- ᴾˢʸᶜʰᵒ", parsed["message"])
        self.assertIn("Title\nA < B & C > D", parsed["message"])
        bold_entity = next(entity for entity in parsed["entities"] if type(entity).__name__ == "MessageEntityBold")
        self.assertEqual(bold_entity.length, len("Title"))

    async def test_user_mentions_are_html_links(self):
        parsed = await HTML(None).parse(
            format_response(
                "Targets\n"
                + format_mentions(
                    [123, 456],
                    command_registry.MSG_USER_MENTION_LINK,
                    command_registry.MSG_MENTIONS_SEPARATOR,
                )
            )
        )
        mention_entities = [
            entity for entity in parsed["entities"]
            if type(entity).__name__ == "InputMessageEntityMentionName"
        ]
        self.assertEqual(len(mention_entities), 2)

    async def test_reaction_uses_raw_fallback_when_wrappers_fail(self):
        class Client:
            async def send_reaction(self, *args, **kwargs):
                raise TypeError("wrapper signature differs")

            async def resolve_peer(self, chat_id):
                return "resolved-peer"

            async def invoke(self, request):
                self.request = request

        client = Client()
        message = SimpleNamespace(chat=SimpleNamespace(id=-100123), id=45)
        self.assertTrue(await _apply_reaction(client, message, "👍"))
        self.assertEqual(type(client.request).__name__, "SendReaction")
        self.assertEqual(client.request.msg_id, 45)

    async def test_list_reactions_shows_users_with_their_emojis(self):
        class Client:
            async def get_users(self, uid):
                return SimpleNamespace(
                    first_name=f"User {uid}", last_name=None, username=None
                )

            async def edit_message_text(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        app = FakeApp()
        setup_reaction_commands(app)
        handler = next(
            callback for callback, _, _ in app.handlers
            if callback.__name__ == "list_reactions"
        )
        client = Client()
        message = SimpleNamespace(
            text=".لیست ریاکشن",
            chat=SimpleNamespace(id=777),
            id=12,
            _client=client,
            edit=None,
            reply=None,
        )
        previous_reactions = state.REACTIONS.copy()
        try:
            state.REACTIONS.clear()
            state.REACTIONS.update({"123": "👍", "456": "🔥"})
            await handler(client, message)
        finally:
            state.REACTIONS.clear()
            state.REACTIONS.update(previous_reactions)

        response = client.args[2]
        self.assertIn("User 123", response)
        self.assertIn("👍", response)
        self.assertIn("User 456", response)
        self.assertIn("🔥", response)

    async def test_saved_messages_match_me_filter_not_catchall(self):
        app = FakeApp()
        setup_message_handler(app)
        catchall_filter = next(
            filters for callback, filters, _ in app.handlers
            if callback.__name__ == "handle_message"
        )
        saved_message = SimpleNamespace(
            chat=SimpleNamespace(id=123456, usernames=None, username=None, type="private"),
            from_user=SimpleNamespace(id=123456, is_self=True, is_bot=False, username=None),
            sender_chat=None,
            outgoing=False,
        )
        self.assertTrue(await filters.chat("me")(None, saved_message))
        self.assertFalse(await catchall_filter(None, saved_message))

    async def test_edit_failure_logs_and_uses_reply_fallback(self):
        class Client:
            async def edit_message_text(self, *args, **kwargs):
                raise RuntimeError("edit denied")

        class Message:
            chat = SimpleNamespace(id=123)
            id = 5
            _client = Client()

            async def edit(self, *args, **kwargs):
                raise RuntimeError("bound edit denied")

            async def reply(self, text, **kwargs):
                self.reply_text = text

        message = Message()
        with self.assertLogs("utils.helpers", level="ERROR") as captured:
            self.assertTrue(await edit_or_reply(message, "result"))
        self.assertTrue(any("edit denied" in line for line in captured.output))
        self.assertIn("result", message.reply_text)

    async def test_headless_session_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir, "selected.session")
            session_file.touch()
            with patch.object(main, "SESSION_DIR", temp_dir), \
                    patch.dict(os.environ, {"SESSION_FILE": "selected"}), \
                    patch("sys.stdin.isatty", return_value=False):
                self.assertEqual(await main.choose_session(), str(session_file.with_suffix("")))

    async def test_interactive_selection_can_override_session_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for session_name in ("default", "wanted"):
                Path(temp_dir, f"{session_name}.session").touch()
            with patch.object(main, "SESSION_DIR", temp_dir), \
                    patch.dict(os.environ, {"SESSION_FILE": "default"}), \
                    patch("sys.stdin.isatty", return_value=True), \
                    patch("builtins.input", return_value="2"):
                selected = await main.choose_session()
            self.assertEqual(selected, str(Path(temp_dir, "wanted")))

    async def test_new_session_menu_option_does_not_reuse_configured_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "default.session").touch()
            with patch.object(main, "SESSION_DIR", temp_dir), \
                    patch.dict(os.environ, {"SESSION_FILE": "default"}), \
                    patch("sys.stdin.isatty", return_value=True), \
                    patch("builtins.input", return_value="0"), \
                    patch.object(main, "create_session", return_value=None) as create:
                await main.choose_session()
            create.assert_awaited_once_with()

    def test_invalid_session_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir, "old.session")
            connection = sqlite3.connect(session_file)
            try:
                connection.execute("CREATE TABLE version (id INTEGER)")
            finally:
                connection.close()
            self.assertFalse(main.ensure_session(str(session_file)))
            self.assertTrue(session_file.exists())
            self.assertFalse(Path(f"{session_file}.old").exists())

    def test_all_help_menu_sections_exist(self):
        overview = command_registry.build_help_text()
        for section in (
            "enemy", "spam", "autospam", "autospam mention", "mute", "reaction",
            "save", "id", "time", "status", "ping",
        ):
            with self.subTest(section=section):
                section_text = command_registry.build_help_section_text(section)
                self.assertIn("<b>", section_text)
                self.assertIn("- ᴾˢʸᶜʰᵒ", section_text)
        self.assertIn("این منو راهنمای دستورهای بات است", overview)
        self.assertIn("<blockquote>", overview)
        self.assertIn("- ᴾˢʸᶜʰᵒ", overview)
        self.assertIn("@نام‌کاربری", command_registry.build_help_section_text("enemy"))
        self.assertIn("ریپلای", command_registry.build_help_section_text("enemy"))

    def test_help_bot_keyboard_has_sections_and_back(self):
        menu = build_help_keyboard()
        labels = [button.text for row in menu.inline_keyboard for button in row]
        self.assertIn("انمی", labels)
        self.assertIn("اتو اسپم منشن", labels)
        self.assertEqual(len(labels), len(command_registry.help_section_names()))
        section = build_help_keyboard("enemy")
        self.assertEqual(section.inline_keyboard[0][0].text, "برگشت")
        self.assertEqual(section.inline_keyboard[0][0].callback_data, "help:home")

    async def test_group_help_sends_inline_menu_into_same_group(self):
        class Client:
            async def get_inline_bot_results(self, bot, query):
                self.bot = bot
                self.query = query
                return SimpleNamespace(
                    query_id=42,
                    results=[SimpleNamespace(id="help-menu-result")],
                )

            async def send_inline_bot_result(self, chat_id, query_id, result_id, **kwargs):
                self.sent = (chat_id, query_id, result_id, kwargs)

            async def edit_message_text(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        async def delete_command():
            message.deleted = True

        app = FakeApp()
        setup_basic_commands(app)
        handler = next(callback for callback, _, _ in app.handlers if callback.__name__ == "help_cmd")
        client = Client()
        group_id = -1009876543210
        message = SimpleNamespace(
            text=".راهنما",
            chat=SimpleNamespace(id=group_id, type="supergroup"),
            id=31,
            _client=client,
            edit=None,
            reply=None,
            delete=delete_command,
        )
        previous_values = (state.OWNER_ID, state.HELP_BOT_USERNAME, state.HELP_BOT_CLIENT)
        state.OWNER_ID = 777
        state.HELP_BOT_USERNAME = "example_help_bot"
        state.HELP_BOT_CLIENT = object()
        try:
            await handler(client, message)
        finally:
            state.OWNER_ID, state.HELP_BOT_USERNAME, state.HELP_BOT_CLIENT = previous_values
        self.assertEqual(client.bot, "example_help_bot")
        self.assertEqual(client.query, ".راهنما")
        self.assertEqual(client.sent[0:3], (group_id, 42, "help-menu-result"))
        self.assertEqual(client.sent[3]["message_thread_id"], None)
        self.assertIsNone(getattr(client, "args", None))
        self.assertTrue(message.deleted)

    async def test_saved_messages_help_inserts_inline_result_into_self_chat(self):
        class Client:
            async def get_inline_bot_results(self, bot, query):
                return SimpleNamespace(query_id=7, results=[SimpleNamespace(id="menu")])

            async def send_inline_bot_result(self, chat_id, query_id, result_id, **kwargs):
                self.sent = (chat_id, query_id, result_id, kwargs)

            async def edit_message_text(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        async def delete_command():
            message.deleted = True

        app = FakeApp()
        setup_basic_commands(app)
        handler = next(callback for callback, _, _ in app.handlers if callback.__name__ == "help_cmd")
        client = Client()
        message = SimpleNamespace(
            text=".راهنما",
            chat=SimpleNamespace(id=777, type="private"),
            id=19,
            message_thread_id=None,
            _client=client,
            edit=None,
            reply=None,
            delete=delete_command,
        )
        previous_values = (state.OWNER_ID, state.HELP_BOT_USERNAME, state.HELP_BOT_CLIENT)
        state.OWNER_ID = 777
        state.HELP_BOT_USERNAME = "example_help_bot"
        state.HELP_BOT_CLIENT = object()
        try:
            await handler(client, message)
        finally:
            state.OWNER_ID, state.HELP_BOT_USERNAME, state.HELP_BOT_CLIENT = previous_values
        self.assertEqual(client.sent[:3], ("me", 7, "menu"))
        self.assertTrue(message.deleted)
        self.assertIsNone(getattr(client, "args", None))

    async def test_help_without_connected_bot_reports_problem_not_plain_menu(self):
        class Client:
            async def edit_message_text(self, *args, **kwargs):
                self.args = args

        app = FakeApp()
        setup_basic_commands(app)
        handler = next(callback for callback, _, _ in app.handlers if callback.__name__ == "help_cmd")
        client = Client()
        message = SimpleNamespace(
            text=".راهنما",
            chat=SimpleNamespace(id=777),
            id=3,
            _client=client,
            edit=None,
            reply=None,
        )
        previous_client, previous_username = state.HELP_BOT_CLIENT, state.HELP_BOT_USERNAME
        state.HELP_BOT_CLIENT = None
        state.HELP_BOT_USERNAME = None
        try:
            await handler(client, message)
        finally:
            state.HELP_BOT_CLIENT, state.HELP_BOT_USERNAME = previous_client, previous_username
        self.assertIn("بات راهنما متصل نیست", client.args[2])
        self.assertNotIn("help enemy", client.args[2])

    def test_help_bot_registers_message_and_callback_handlers(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)
        self.assertEqual([callback.__name__ for callback, _, _ in app.handlers], ["show_help"])
        self.assertEqual([callback.__name__ for callback, _, _ in app.inline_handlers], ["inline_help"])
        self.assertEqual(
            [callback.__name__ for callback, _, _ in app.callback_handlers],
            ["handle_help_callback"],
        )

    async def test_inline_query_returns_menu_or_requested_section(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)
        inline_help = app.inline_handlers[0][0]

        class InlineQuery:
            from_user = SimpleNamespace(id=123)

            def __init__(self, query):
                self.id = f"query-{query}"
                self.query = query

        async def answer_inline_query(query_id, results, **kwargs):
            app.last_answer = (query_id, results, kwargs)

        app.answer_inline_query = answer_inline_query
        await inline_help(app, InlineQuery(".راهنما"))
        _, menu_results, options = app.last_answer
        self.assertTrue(menu_results)
        self.assertIsInstance(menu_results[0], InlineQueryResultArticle)
        self.assertEqual(len(menu_results[0].reply_markup.inline_keyboard), 6)
        menu_text = menu_results[0].input_message_content.message_text
        self.assertIn("<blockquote>", menu_text)
        self.assertIn("دکمه هر بخش", menu_text)
        self.assertIn("- ᴾˢʸᶜʰᵒ", menu_text)
        self.assertNotIn("-Void", menu_text)
        self.assertEqual(options["is_personal"], True)

        await inline_help(app, InlineQuery(".راهنما انمی"))
        _, section_results, _ = app.last_answer
        self.assertIn("انمی", section_results[0].title)
        section_text = section_results[0].input_message_content.message_text
        self.assertIn("راهنمای انمی", section_text)
        self.assertIn("<code>.انمی</code>", section_text)
        self.assertIn("<blockquote>", section_text)
        self.assertIn("- ᴾˢʸᶜʰᵒ", section_text)

    async def test_inline_query_from_non_owner_gets_no_results(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)
        inline_help = app.inline_handlers[0][0]

        class InlineQuery:
            id = "private-query"
            query = ".راهنما"
            from_user = SimpleNamespace(id=456)

        async def answer_inline_query(query_id, results, **kwargs):
            app.last_answer = (query_id, results, kwargs)

        app.answer_inline_query = answer_inline_query
        await inline_help(app, InlineQuery())
        self.assertEqual(app.last_answer[1], [])
        self.assertEqual(app.last_answer[2]["is_personal"], True)

    async def test_help_bot_silently_ignores_non_owner_start(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)
        show_help = app.handlers[0][0]

        class Message:
            from_user = SimpleNamespace(id=456)
            replied = False

            async def reply_text(self, *args, **kwargs):
                self.replied = True

        message = Message()
        await show_help(app, message)
        self.assertFalse(message.replied)

    async def test_help_bot_callback_edits_section_and_answers_query(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)
        callback = app.callback_handlers[0][0]

        class CallbackMessage:
            async def edit_text(self, text, **kwargs):
                self.text = text
                self.kwargs = kwargs

        class CallbackQuery:
            from_user = SimpleNamespace(id=123)
            matches = [SimpleNamespace(group=lambda _: "enemy")]
            message = CallbackMessage()

            async def answer(self, *args, **kwargs):
                self.answered = True

        query = CallbackQuery()
        await callback(app, query)
        self.assertIn("راهنمای انمی", query.message.text)
        self.assertIn("- ᴾˢʸᶜʰᵒ", query.message.text)
        self.assertEqual(query.message.kwargs["reply_markup"].inline_keyboard[0][0].text, "برگشت")
        self.assertTrue(query.answered)

    async def test_inline_callback_edits_message_in_place(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)

        class CallbackQuery:
            from_user = SimpleNamespace(id=123)
            inline_message_id = "inline-message-id"
            message = None
            matches = [SimpleNamespace(group=lambda _: "enemy")]

            async def answer(self, *args, **kwargs):
                self.answered = True

        async def edit_inline_text(inline_message_id, text, **kwargs):
            app.edited = (inline_message_id, text, kwargs)

        app.edit_inline_text = edit_inline_text
        query = CallbackQuery()
        await app.callback_handlers[0][0](app, query)
        self.assertEqual(app.edited[0], "inline-message-id")
        self.assertIn("راهنمای انمی", app.edited[1])
        self.assertIn("- ᴾˢʸᶜʰᵒ", app.edited[1])
        self.assertTrue(query.answered)

    async def test_help_bot_rejects_non_owner_callbacks(self):
        app = FakeApp()
        setup_help_bot(app, owner_id=123)

        class CallbackQuery:
            from_user = SimpleNamespace(id=456)
            matches = [SimpleNamespace(group=lambda _: "help:enemy")]
            message = None

            async def answer(self, text=None, show_alert=False):
                self.answer_text = text
                self.show_alert = show_alert

        query = CallbackQuery()
        await app.callback_handlers[0][0](app, query)
        self.assertIsNone(query.answer_text)
        self.assertFalse(query.show_alert)

    def test_command_handlers_do_not_reply_directly(self):
        root = Path(__file__).resolve().parents[1] / "commands"
        for source_file in root.glob("*.py"):
            source = source_file.read_text(encoding="utf-8")
            self.assertNotRegex(source, r"message\.(?:reply|reply_text)\(")

    def test_message_command_handlers_use_central_edit_helper(self):
        root = Path(__file__).resolve().parents[1] / "commands"
        missing_helper = []
        for source_file in root.glob("*.py"):
            tree = ast.parse(source_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                    continue
                is_message_handler = any(
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "on_message"
                    for decorator in node.decorator_list
                )
                if is_message_handler and not any(
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Name)
                    and child.func.id == "edit_or_reply"
                    for child in ast.walk(node)
                ):
                    missing_helper.append(f"{source_file.name}:{node.name}")
        self.assertEqual(missing_helper, [])

    def test_enemy_and_reaction_settings_persist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Database(str(Path(temp_dir, "session.db.json")))
            with patch("utils.state.db", database):
                from utils.state import State

                current_state = State()
                current_state.add_enemy(123456, "A < B & C > D")
                current_state.set_reaction(123456, "👍")
                restarted_state = State()
            self.assertIn(123456, restarted_state.ENEMIES)
            self.assertEqual(restarted_state.ENEMY_RESPONSES["123456"], "A < B & C > D")
            self.assertEqual(restarted_state.REACTIONS["123456"], "👍")


if __name__ == "__main__":
    unittest.main()