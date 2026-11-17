import re

CMD_HELP_NAMES = ["راهنما"]
CMD_STATUS_NAMES = ["لیست کلی"]
CMD_PING_NAMES = ["پینگ"]

CMD_ENEMY_NAMES = ["انمی"]
CMD_REMOVE_ENEMY_NAMES = ["حذف انمی"]
CMD_LIST_ENEMY_NAMES = ["لیست انمی"]
CMD_CLEAR_ENEMY_NAMES = ["پاکسازی انمی"]

CMD_SPAM_NAMES = ["اسپم"]
CMD_REMOVE_SPAM_NAMES = ["حذف اسپم"]
CMD_LIST_SPAM_NAMES = ["لیست اسپم"]
CMD_CLEAR_SPAM_NAMES = ["پاکسازی اسپم"]

CMD_AUTOSPAM_NAMES = ["اتو اسپم"]
CMD_REMOVE_AUTOSPAM_NAMES = ["حذف اتو"]
CMD_LIST_AUTOSPAM_NAMES = ["لیست اتو"]
CMD_CLEAR_AUTOSPAM_NAMES = ["پاکسازی اتو"]

CMD_AUTOSPAM_MENTION_NAMES = ["اتو اسپم منشن",]
CMD_REMOVE_AUTOSPAM_MENTION_NAMES = ["حذف اتو منشن"]
CMD_LIST_AUTOSPAM_MENTION_NAMES = ["لیست اتو منشن"]
CMD_CLEAR_AUTOSPAM_MENTION_NAMES = ["پاکسازی اتو منشن"]

CMD_MUTE_NAMES = ["میوت"]
CMD_REMOVE_MUTE_NAMES = ["حذف میوت"]
CMD_LIST_MUTE_NAMES = ["لیست میوت"]
CMD_CLEAR_MUTE_NAMES = ["پاکسازی میوت"]

CMD_REACTION_NAMES = ["ریاکشن"]
CMD_REMOVE_REACTION_NAMES = ["حذف ریاکشن"]
CMD_LIST_REACTION_NAMES = ["لیست ریاکشن", "نمایش ریاکشن"]
CMD_CLEAR_REACTION_NAMES = ["پاکسازی ریاکشن"]
CMD_AVAILABLE_REACTIONS_NAMES = ['ریاکشن های موجود']

CMD_SET_TIME_NAMES = ["تنظیم ساعت"]
CMD_DEL_TIME_NAMES = ["حذف ساعت"]

CMD_SAVE_NAMES = ["سیو"]
CMD_ID_NAMES = ["ایدی"]
CMD_USERID_NAMES = ["آیدی", "آی دی"]

COMMAND_PREFIX = "."
CMD_NAME_GROUPS = (
    CMD_HELP_NAMES,
    CMD_STATUS_NAMES,
    CMD_PING_NAMES,
    CMD_ENEMY_NAMES,
    CMD_REMOVE_ENEMY_NAMES,
    CMD_LIST_ENEMY_NAMES,
    CMD_CLEAR_ENEMY_NAMES,
    CMD_SPAM_NAMES,
    CMD_REMOVE_SPAM_NAMES,
    CMD_LIST_SPAM_NAMES,
    CMD_CLEAR_SPAM_NAMES,
    CMD_AUTOSPAM_NAMES,
    CMD_REMOVE_AUTOSPAM_NAMES,
    CMD_LIST_AUTOSPAM_NAMES,
    CMD_CLEAR_AUTOSPAM_NAMES,
    CMD_AUTOSPAM_MENTION_NAMES,
    CMD_REMOVE_AUTOSPAM_MENTION_NAMES,
    CMD_LIST_AUTOSPAM_MENTION_NAMES,
    CMD_CLEAR_AUTOSPAM_MENTION_NAMES,
    CMD_MUTE_NAMES,
    CMD_REMOVE_MUTE_NAMES,
    CMD_LIST_MUTE_NAMES,
    CMD_CLEAR_MUTE_NAMES,
    CMD_REACTION_NAMES,
    CMD_REMOVE_REACTION_NAMES,
    CMD_LIST_REACTION_NAMES,
    CMD_CLEAR_REACTION_NAMES,
    CMD_AVAILABLE_REACTIONS_NAMES,
    CMD_SET_TIME_NAMES,
    CMD_DEL_TIME_NAMES,
    CMD_SAVE_NAMES,
    CMD_ID_NAMES,
    CMD_USERID_NAMES,
)
COMMAND_SKIP_PREFIXES = tuple(
    f"{COMMAND_PREFIX}{name}"
    for names in CMD_NAME_GROUPS
    for name in names
)


def _command_pattern(names, arg_pattern=None, multi_args=False, disallow_after=None):
    name_pattern = "|".join(re.escape(name) for name in names)
    if disallow_after:
        disallow_pattern = "|".join(re.escape(name) for name in disallow_after)
        prefix = rf"^\.(?:{name_pattern})(?!\s+(?:{disallow_pattern}))"
    else:
        prefix = rf"^\.(?:{name_pattern})"

    if arg_pattern is None:
        return rf"(?i){prefix}(?:\s*)$"
    if multi_args:
        return rf"(?i){prefix}(?:$|\s+(?:{arg_pattern})(?:\s+(?:{arg_pattern}))*\s*)$"
    return rf"(?i){prefix}(?:$|\s+(?:{arg_pattern})\s*)$"

USERNAME_ID_TOKEN = r"(?:@\w+|-?\d+)"

CMD_HELP = _command_pattern(CMD_HELP_NAMES, arg_pattern=r".*", multi_args=True)
CMD_STATUS = _command_pattern(CMD_STATUS_NAMES)
CMD_PING = _command_pattern(CMD_PING_NAMES)

CMD_ENEMY = _command_pattern(CMD_ENEMY_NAMES, arg_pattern=r".*")
CMD_REMOVE_ENEMY = _command_pattern(CMD_REMOVE_ENEMY_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_LIST_ENEMY = _command_pattern(CMD_LIST_ENEMY_NAMES)
CMD_CLEAR_ENEMY = _command_pattern(CMD_CLEAR_ENEMY_NAMES)

CMD_SPAM = _command_pattern(CMD_SPAM_NAMES, arg_pattern=r".+")
CMD_REMOVE_SPAM = _command_pattern(CMD_REMOVE_SPAM_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_LIST_SPAM = _command_pattern(CMD_LIST_SPAM_NAMES)
CMD_CLEAR_SPAM = _command_pattern(CMD_CLEAR_SPAM_NAMES)

CMD_AUTOSPAM = _command_pattern(
    CMD_AUTOSPAM_NAMES,
    arg_pattern=USERNAME_ID_TOKEN,
    disallow_after=["منشن"],
)
CMD_REMOVE_AUTOSPAM = _command_pattern(CMD_REMOVE_AUTOSPAM_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_LIST_AUTOSPAM = _command_pattern(CMD_LIST_AUTOSPAM_NAMES)
CMD_CLEAR_AUTOSPAM = _command_pattern(CMD_CLEAR_AUTOSPAM_NAMES)

CMD_AUTOSPAM_MENTION = _command_pattern(
    CMD_AUTOSPAM_MENTION_NAMES,
    arg_pattern=USERNAME_ID_TOKEN,
    multi_args=True,
)
CMD_REMOVE_AUTOSPAM_MENTION = _command_pattern(
    CMD_REMOVE_AUTOSPAM_MENTION_NAMES,
    arg_pattern=USERNAME_ID_TOKEN,
    multi_args=True,
)
CMD_LIST_AUTOSPAM_MENTION = _command_pattern(CMD_LIST_AUTOSPAM_MENTION_NAMES)
CMD_CLEAR_AUTOSPAM_MENTION = _command_pattern(CMD_CLEAR_AUTOSPAM_MENTION_NAMES)

CMD_MUTE = _command_pattern(CMD_MUTE_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_REMOVE_MUTE = _command_pattern(CMD_REMOVE_MUTE_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_LIST_MUTE = _command_pattern(CMD_LIST_MUTE_NAMES)
CMD_CLEAR_MUTE = _command_pattern(CMD_CLEAR_MUTE_NAMES)

CMD_REACTION = _command_pattern(
    CMD_REACTION_NAMES,
    arg_pattern=r".+",
    disallow_after=["های قابل استفاده", "های موجود"],
)
CMD_REMOVE_REACTION = _command_pattern(CMD_REMOVE_REACTION_NAMES, arg_pattern=USERNAME_ID_TOKEN)
CMD_LIST_REACTION = _command_pattern(CMD_LIST_REACTION_NAMES)
CMD_CLEAR_REACTION = _command_pattern(CMD_CLEAR_REACTION_NAMES)
CMD_AVAILABLE_REACTIONS = _command_pattern(CMD_AVAILABLE_REACTIONS_NAMES)

CMD_SET_TIME = _command_pattern(CMD_SET_TIME_NAMES)
CMD_DEL_TIME = _command_pattern(CMD_DEL_TIME_NAMES)

CMD_SAVE = _command_pattern(CMD_SAVE_NAMES, arg_pattern=r".*", multi_args=True)
CMD_ID = _command_pattern(CMD_ID_NAMES, arg_pattern=r".*")
CMD_USERID = _command_pattern(CMD_USERID_NAMES, arg_pattern=r".*")

HELP_ENTRYPOINT = f"{COMMAND_PREFIX}{CMD_HELP_NAMES[0]}"
HELP_ENTRY_PATTERN = rf"^{re.escape(COMMAND_PREFIX)}(?:{'|'.join(map(re.escape, CMD_HELP_NAMES))})$"
HELP_CALLBACK_PREFIX = "help:"
HELP_CALLBACK_HOME = "help:home"
HELP_CALLBACK_PATTERN = rf"^{re.escape(HELP_CALLBACK_PREFIX)}(.+)$"
HELP_BACK_LABEL = "برگشت"
HELP_SECTION_LABELS = {
    "enemy": "انمی",
    "spam": "اسپم",
    "autospam": "اتو اسپم",
    "autospam mention": "اتو اسپم منشن",
    "mute": "میوت",
    "reaction": "ریاکشن",
    "save": "ذخیره",
    "id": "شناسه",
    "time": "ساعت",
    "status": "فهرست کلی",
    "ping": "پینگ",
}
HELP_INLINE_QUERY_PREFIX = f"{HELP_ENTRYPOINT} "

MSG_USAGE_ENEMY = "روش استفاده از انمی\nروی پیام هدف ریپلای کن یا شناسه و متن پاسخ را بعد از دستور بنویس."
MSG_USAGE_REMOVE_ENEMY = "روش حذف انمی\nروی پیام هدف ریپلای کن یا شناسه و نام کاربری را بعد از دستور بنویس."
MSG_LIST_ENEMY_EMPTY = "فهرست انمی خالی است."
MSG_ENEMY_CLEARED = "همه تنظیم‌های انمی پاک شدند."
MSG_ENEMY_RANDOM_RESPONSE = "پاسخ تصادفی از فایل پاسخ‌ها"
MSG_ENEMY_KIND_CUSTOM = "اختصاصی"
MSG_ENEMY_KIND_RANDOM = "تصادفی"
MSG_ENEMY_ADDED_CONFIRMATION = (
    "انمی فعال شد\nکاربر: {label}\nنوع پاسخ: {kind}\nمتن پاسخ: {response}"
)
MSG_ENEMY_REMOVED_CONFIRMATION = "انمی غیرفعال شد\nکاربر: {label}"
MSG_ENEMY_LIST_TITLE = "فهرست انمی"
MSG_ENEMY_LIST_ITEM = "• {label}\nنوع پاسخ: {kind}{response_text}"
MSG_ENEMY_LIST_RESPONSE = "\nمتن پاسخ: {response}"

MSG_USAGE_SPAM = "روش استفاده از اسپم\nمتن و تعداد پیام‌ها را بنویس. برای تعیین هدف، روی پیام او ریپلای کن یا نام کاربری‌اش را وارد کن."
MSG_USAGE_REMOVE_SPAM = "روش حذف اسپم\nروی پیام هدف ریپلای کن یا شناسه او را بعد از دستور بنویس."
MSG_SPAM_REMOVED = "تنظیم اسپم برای شناسه {uid} حذف شد."
MSG_LIST_SPAM_EMPTY = "فهرست اسپم خالی است."
MSG_SPAM_CLEARED = "همه تنظیم‌های اسپم پاک شدند."
MSG_SPAM_IN_PROGRESS = "ارسال اسپم آغاز شد\nتعداد پیام‌ها: {count}"
MSG_SPAM_LIST_TITLE = "فهرست اسپم\n"

MSG_USAGE_AUTOSPAM = "روش استفاده از اتو اسپم\nروی پیام هدف ریپلای کن یا شناسه او را بعد از دستور بنویس."
MSG_USAGE_REMOVE_AUTOSPAM = "روش توقف اتو اسپم\nروی پیام هدف ریپلای کن یا شناسه او را بعد از دستور بنویس."
MSG_AUTOSPAM_ALREADY_RUNNING = "اتو اسپم برای این کاربر از قبل فعال است."
MSG_AUTOSPAM_STARTED = "اتو اسپم فعال شد\nشناسه کاربر: {uid}"
MSG_AUTOSPAM_STOPPED = "اتو اسپم غیرفعال شد\nشناسه کاربر: {uid}"
MSG_LIST_AUTOSPAM_EMPTY = "فهرست اتو اسپم خالی است."
MSG_AUTOSPAM_CLEARED = "همه تنظیم‌های اتو اسپم پاک شدند."
MSG_AUTOSPAM_LIST_TITLE = "فهرست اتو اسپم\n"

MSG_USAGE_AUTOSPAM_MENTION = "روش استفاده از اتو اسپم منشن\nروی پیام هدف ریپلای کن یا شناسه و نام کاربری هدف‌ها را بعد از دستور بنویس."
MSG_AUTOSPAM_MENTION_ALREADY_RUNNING = "اتو اسپم منشن از قبل فعال است."
MSG_AUTOSPAM_MENTION_STARTED = "اتو اسپم منشن فعال شد\nهدف‌ها: {mentions}"
MSG_AUTOSPAM_MENTION_NOT_FOUND = "هیچ هدف معتبری پیدا نشد. شناسه یا نام کاربری را بررسی کن."
MSG_AUTOSPAM_MENTION_REMOVED = "اتو اسپم منشن غیرفعال شد\nهدف‌ها: {mentions}"
MSG_LIST_AUTOSPAM_MENTION_EMPTY = "فهرست اتو اسپم منشن خالی است."
MSG_AUTOSPAM_MENTION_CLEARED = "همه تنظیم‌های اتو اسپم منشن پاک شدند."
MSG_AUTOSPAM_MENTION_NO_ACTIVE = "برای هدف‌های واردشده اتو اسپم منشن فعالی پیدا نشد."
MSG_AUTOSPAM_MENTION_LIST_TITLE = "فهرست اتو اسپم منشن\n"

MSG_USAGE_MUTE = "روش استفاده از میوت\nروی پیام هدف ریپلای کن یا شناسه او را بعد از دستور بنویس."
MSG_USAGE_REMOVE_MUTE = "روش حذف میوت\nروی پیام هدف ریپلای کن یا شناسه او را بعد از دستور بنویس."
MSG_MUTED_ADDED = "میوت فعال شد\nشناسه کاربر: {uid}"
MSG_MUTED_REMOVED = "میوت برداشته شد\nشناسه کاربر: {uid}"
MSG_LIST_MUTED_EMPTY = "فهرست میوت خالی است."
MSG_MUTED_CLEARED = "همه تنظیم‌های میوت پاک شدند."
MSG_MUTE_LIST_TITLE = "فهرست میوت\n"
MSG_USER_LIST_ITEM = '• <a href="tg://user?id={uid}">{label}</a>\n  شناسه: <code>{uid}</code>'
MSG_USER_MENTION_LINK = '<a href="tg://user?id={uid}">کاربر</a>'
MSG_MENTIONS_SEPARATOR = "، "
MSG_LIST_UID_ITEM = "• {uid}"
RESPONSE_SIGNATURE = "- ᴾˢʸᶜʰᵒ"

MSG_USAGE_REACTION = "روش تنظیم ریاکشن\nروی پیام هدف ریپلای کن یا شناسه او را همراه ایموجی بنویس."
MSG_USAGE_REMOVE_REACTION = "روش حذف ریاکشن\nروی پیام هدف ریپلای کن یا شناسه و نام کاربری او را بعد از دستور بنویس."
MSG_REACTION_SET = "ریاکشن تنظیم شد\nایموجی: {emoji}\nشناسه کاربر: {uid}"
MSG_REACTION_REMOVED = "ریاکشن حذف شد\nشناسه کاربر: {uid}"
MSG_REACTION_CLEARED = "همه ریاکشن‌ها پاک شدند."
MSG_LIST_REACTIONS_EMPTY = "هنوز برای هیچ کاربری ریاکشنی تنظیم نشده است."
MSG_REACTIONS_LIST_TITLE = "ریاکشن‌های تنظیم‌شده\n"
MSG_REACTION_LIST_ITEM = "• {user}\nریاکشن: {emoji}"
MSG_AVAILABLE_REACTIONS_EMPTY = "فهرست ایموجی‌های قابل استفاده در دسترس نیست."
MSG_REACTION_INVALID = "ایموجی معتبر وارد کن."
MSG_AVAILABLE_REACTIONS_TITLE = "ایموجی‌های قابل استفاده\n"
MSG_SET_TIME = "نمایش ساعت روی نام فعال شد."
MSG_DEL_TIME = "نمایش ساعت روی نام غیرفعال شد."

MSG_SAVE_NEEDS_REPLY = "برای ذخیره، روی پیام موردنظر ریپلای کن یا لینک آن را بفرست."
MSG_SAVE_SUCCEEDED = "پیام ذخیره شد."
MSG_SAVE_FAILED = "ذخیره پیام انجام نشد. دوباره تلاش کن."
MSG_ID_USAGE = "برای دیدن شناسه، روی پیام کاربر ریپلای کن یا نام کاربری او را بنویس."
MSG_ID_INFO = "اطلاعات کاربر\nشناسه: <code>{uid}</code>\nنام: <code>{name}</code>"

MSG_BASIC_HELP_DISCONNECTED = "<b>بات راهنما متصل نیست</b>"
MSG_BASIC_HELP_CONNECTION_DETAIL = "\nعلت اتصال: {error}"
MSG_BASIC_HELP_TIMEOUT = "پاسخ راهنما دریافت نشد\nکمی بعد دوباره تلاش کن."
MSG_BASIC_HELP_EMPTY_RESULTS = "راهنما پاسخی برنگرداند\nدرخواست: {query}"
MSG_BASIC_HELP_TELEGRAM_ERROR = "خطای تلگرام: {error_type}: {error}"
MSG_BASIC_HELP_OTHER_ERROR = "خطای {error_type}: {error}"
MSG_BASIC_HELP_INSERT_FAILED = "نمایش منوی راهنما انجام نشد\n{reason}\nتنظیمات اینلاین بات @{username} را بررسی کن."
MSG_BASIC_HELP_CANNOT_EDIT = "این پیام دیگر قابل ویرایش نیست."
MSG_BASIC_HELP_SECTION_NOT_FOUND = "این بخش پیدا نشد."
MSG_BASIC_HELP_SECTION_FAILED = "نمایش این بخش ناموفق بود."
MSG_HELP_INLINE_TITLE = "راهنمای دستورها"
MSG_HELP_INLINE_DESCRIPTION = "راهنمای بخش‌های بات"
MSG_HELP_SECTION_DESCRIPTION = "راهنمای بخش {title}"
MSG_BASIC_STATUS = (
    "گزارش وضعیت\n"
    "انمی: {enemies}\n"
    "اسپم: {spams}\n"
    "اتو اسپم: {auto_spams}\n"
    "میوت: {muted}\n"
    "ریاکشن: {reactions}"
)
MSG_BASIC_PING = "اتصال برقرار است\nبات آماده پاسخ‌گویی است."
MSG_HELP_SECTION_NOT_FOUND = "<b>این بخش پیدا نشد</b>\n"
MSG_HELP_OVERVIEW_TITLE = "<b>راهنمای دستورها</b>\n"
MSG_HELP_OVERVIEW_FOOTER = f"\n\nبرای برگشت، {HELP_ENTRYPOINT} را بفرست."
MSG_HELP_SUPPORT = "پشتیبانی: @MrSudoX"
MSG_HELP_SECTION_TITLE = "<b>راهنمای {title}</b>\n"
MSG_HELP_CANNOT_EDIT = MSG_BASIC_HELP_CANNOT_EDIT
MSG_HELP_SECTION_NOT_FOUND_ALERT = MSG_BASIC_HELP_SECTION_NOT_FOUND
MSG_HELP_SECTION_FAILED_ALERT = MSG_BASIC_HELP_SECTION_FAILED


_HELP_SECTIONS = {
    "enemy": (
        "انمی",
        [
            "انمی برای پاسخ خودکار به پیام‌های یک کاربر است. روی پیام او ریپلای کن و <code>.انمی</code> بفرست.",
            "<blockquote>برای پاسخ اختصاصی، متن را بعد از دستور بنویس. برای پاسخ تصادفی، دستور را بدون متن بفرست.</blockquote>",
            "بدون ریپلای می‌توانی <code>.انمی @نام‌کاربری متن</code> یا <code>.انمی شناسه متن</code> بنویسی.",
            "<code>.حذف انمی</code> انمی را خاموش می‌کند. <code>.لیست انمی</code> فهرست را نشان می‌دهد و <code>.پاکسازی انمی</code> همه را پاک می‌کند.",
        ],
    ),
    "spam": (
        "اسپم",
        [
            "اسپم، متن دلخواه را به تعداد مشخص ارسال می‌کند. از <code>.اسپم متن تعداد</code> استفاده کن.",
            "<blockquote>برای تعیین هدف، روی پیام او ریپلای کن یا نام کاربری‌اش را بنویس.</blockquote>",
            "<code>.حذف اسپم</code> هدف را حذف می‌کند. <code>.لیست اسپم</code> فهرست را نشان می‌دهد و <code>.پاکسازی اسپم</code> همه را پاک می‌کند.",
        ],
    ),
    "autospam": (
        "اتو اسپم",
        [
            "اتو اسپم پاسخ‌های فایل پاسخ‌ها را به‌صورت خودکار می‌فرستد. روی پیام هدف ریپلای کن و <code>.اتو اسپم</code> بفرست.",
            "<blockquote>برای شروع بدون ریپلای، شناسه یا نام کاربری را بعد از دستور بنویس.</blockquote>",
            "<code>.حذف اتو</code> اتو اسپم را متوقف می‌کند. <code>.لیست اتو</code> فهرست را نشان می‌دهد و <code>.پاکسازی اتو</code> همه را پاک می‌کند.",
        ],
    ),
    "autospam mention": (
        "اتو اسپم منشن",
        [
            "اتو اسپم منشن پاسخ خودکار را همراه منشن هدف‌ها می‌فرستد. روی پیام هدف ریپلای کن و <code>.اتو اسپم منشن</code> بفرست.",
            "<blockquote>برای چند هدف، شناسه‌ها یا نام‌های کاربری را بعد از دستور وارد کن.</blockquote>",
            "<code>.حذف اتو منشن</code> هدف‌ها را حذف می‌کند. <code>.لیست اتو منشن</code> فهرست را نشان می‌دهد و <code>.پاکسازی اتو منشن</code> همه را پاک می‌کند.",
        ],
    ),
    "mute": (
        "میوت",
        [
            "میوت پیام‌های کاربر هدف را حذف می‌کند. روی پیام او ریپلای کن و <code>.میوت</code> بفرست.",
            "<blockquote>برای برداشتن میوت از <code>.حذف میوت</code> استفاده کن.</blockquote>",
            "<code>.لیست میوت</code> فهرست را نشان می‌دهد و <code>.پاکسازی میوت</code> همه را پاک می‌کند.",
        ],
    ),
    "reaction": (
        "ریاکشن",
        [
            "برای تنظیم ریاکشن، روی پیام هدف ریپلای کن و <code>.ریاکشن ایموجی</code> بفرست.",
            "<blockquote>برای حذف از <code>.حذف ریاکشن</code> استفاده کن.</blockquote>",
            "<code>.لیست ریاکشن</code> کاربران و ریاکشن تنظیم‌شده برای هرکدام را نشان می‌دهد.",
            "<code>.ریاکشن های موجود</code> ایموجی‌های قابل استفاده را نشان می‌دهد. <code>.پاکسازی ریاکشن</code> همه تنظیم‌ها را پاک می‌کند.",
        ],
    ),
    "save": (
        "ذخیره",
        ["برای ذخیره پیام، روی آن ریپلای کن و <code>.سیو</code> بفرست. در غیر این صورت لینک پیام را همراه دستور ارسال کن."],
    ),
    "id": (
        "شناسه",
        ["برای دیدن شناسه، روی پیام ریپلای کن و <code>.ایدی</code> بفرست. نام کاربری را هم می‌توانی بعد از دستور بنویسی."],
    ),
    "time": (
        "ساعت",
        ["<code>.تنظیم ساعت</code> ساعت را روی نام حساب نمایش می‌دهد. <code>.حذف ساعت</code> آن را خاموش می‌کند."],
    ),
    "status": (
        "وضعیت",
        ["<code>.لیست کلی</code> تعداد تنظیم‌های فعال انمی، اسپم، اتو اسپم، میوت و ریاکشن را گزارش می‌دهد."],
    ),
    "ping": (
        "پینگ",
        ["<code>.پینگ</code> بررسی می‌کند که بات آماده پاسخ‌گویی است."],
    ),
}

_HELP_ALIASES = {
    "انمی": "enemy",
    "اسپم": "spam",
    "اتو اسپم": "autospam",
    "اتو اسپم منشن": "autospam mention",
    "میوت": "mute",
    "ریاکشن": "reaction",
    "سیو": "save",
    "آیدی": "id",
    "آی دی": "id",
    "ساعت": "time",
    "تنظیم ساعت": "time",
    "وضعیت": "status",
    "پینگ": "ping",
    "راهنما": "",
    "کمک": "",
    "هلپ": "",
}


def help_section_names():
    return tuple(_HELP_SECTIONS)


def resolve_help_section(section_name: str):
    section_name = " ".join((section_name or "").strip().lower().split())
    return _HELP_ALIASES.get(section_name, section_name)


def build_help_text():
    return (
        MSG_HELP_OVERVIEW_TITLE
        + "این منو راهنمای دستورهای بات است. دکمه هر بخش را بزن تا کاربرد و روش استفاده‌اش را ببینی.\n"
        + "<blockquote>برای برگشت به این صفحه، دکمه برگشت را بزن.</blockquote>"
        + f"\n{MSG_HELP_SUPPORT}"
        + f"\n<b>{RESPONSE_SIGNATURE}</b>"
    )


def build_help_section_text(section_name: str):
    section_name = resolve_help_section(section_name)
    if not section_name:
        return build_help_text()

    section = _HELP_SECTIONS.get(section_name)
    if section is None:
        return MSG_HELP_SECTION_NOT_FOUND + build_help_text()

    title, lines = section
    return (
        MSG_HELP_SECTION_TITLE.format(title=title)
        + "\n".join(lines)
        + f"\n<b>{RESPONSE_SIGNATURE}</b>"
    )
