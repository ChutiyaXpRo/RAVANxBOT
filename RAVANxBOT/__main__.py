import importlib
import time
import re
from sys import argv
from typing import Optional

from RAVANxBOT import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from RAVANxBOT.modules import ALL_MODULES
from RAVANxBOT.modules.helper_funcs.chat_status import is_user_admin
from RAVANxBOT.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
[💖](https://telegra.ph/file/8b89db5b068c56aba4217.png)
𝗛𝗶𝗶, 𝗧𝗵𝗶𝘀 𝗶𝘀 **[𝗭𝗲𝗽𝗵𝘆𝗿](http://t.me/ZephyrManagerBot)
𝗜'𝗺 𝗵𝗲𝗿𝗲 𝘁𝗼 𝗵𝗲𝗹𝗽 𝗺𝗮𝗻𝗮𝗴𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽𝘀 .𝗔𝗱𝗱 𝗺𝗲 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 𝗳𝗼𝗿 𝗺𝗼𝗿𝗲 𝘂𝘀𝗮𝗴𝗲 & 𝘁𝘆𝗽𝗲 /help 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗹𝗶𝘀𝘁 𝗼𝗳 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 . 
"""

buttons = [
    [
        InlineKeyboardButton(
            text="𝗔𝗱𝗱 𝗺𝗲 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 💞", url="t.me/ZephyrManagerBot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="𝗦𝗼𝘂𝗿𝗰𝗲 ✨", url=f"https://github.com/Dhruvxbhudev2/YoneRobot"),
        InlineKeyboardButton(
            text="𝗦𝘂𝗽𝗽𝗼𝗿𝘁 💖", url=f"https://t.me/ZephyrProjects"
        ),
    ],
    [
        InlineKeyboardButton(text="𝗖𝗵𝗮𝘁𝘁𝗶𝗻𝗴 💫", url=f"https://t.me/princegehlot2"),
        InlineKeyboardButton(
            text="♡︎ 𝗢𝘄𝗻𝗲𝗿 ♡︎ ", url=f"https://t.me/TheZephyrz"
        ),
    ],
    [
        InlineKeyboardButton(text="𝗛𝗲𝗹𝗽 ❣️", callback_data="help_back"),
    ],
]


HELP_STRINGS = """
𝗬𝗼𝘂 𝗰𝗮𝗻 𝗰𝗵𝗼𝗼𝘀𝗲 𝗮𝗻𝘆 𝗼𝗽𝘁𝗶𝗼𝗻 𝗯𝘆 𝗰𝗹𝗶𝗰𝗸𝗶𝗻𝗴 𝗳𝗿𝗼𝗺 𝗯𝗲𝗹𝗼𝘄 .
𝗜𝗳 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝗻𝘆 𝗵𝗲𝗹𝗽 𝘆𝗼𝘂 𝗰𝗮𝗻 𝗱𝗺 𝘁𝗼 𝘁𝗵𝗲 [𝗢𝘄𝗻𝗲𝗿](https://t.me/TheZephyrz) [❤️](https://telegra.ph/file/956e943a3ebbd1c888d2f.mp4)"""

START_IMG = "https://telegra.ph/file/185c99bcb4418780b0d62.jpg"

DONATE_STRING = """𝗛𝗲𝘆𝗮, 𝗴𝗹𝗮𝗱 𝘁𝗼 𝗵𝗲𝗮𝗿 𝘁𝗵𝗮𝘁 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗱𝗼𝗻𝗮𝘁𝗲 💞!
 𝗬𝗼𝘂 𝗰𝗮𝗻 𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝘁𝗵𝗲 𝗽𝗿𝗼𝗷𝗲𝗰𝘁 𝗵𝗲𝗿𝗲 [𝗢𝘄𝗻𝗲𝗿♡︎](https://t.me/FinalStrikeOp) \
 𝗦𝘂𝗽𝗽𝗼𝗿𝘁𝗶𝗻𝗴 𝗶𝘀𝗻'𝘁 𝗮𝗹𝘄𝗮𝘆𝘀 𝗳𝗶𝗻𝗮𝗻𝗰𝗶𝗮𝗹 💖! [ 𝗡𝗲𝘁𝘄𝗼𝗿𝗸 ](https://t.me/ZephyrXNetwork) \
 𝗧𝗵𝗼𝘀𝗲 𝘄𝗵𝗼 𝗰𝗮𝗻 𝗻𝗼𝘁 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝗺𝗼𝗻𝗲𝘁𝗮𝗿𝘆. 𝗬𝗼𝘂 𝗰𝗮𝗻 𝘀𝘂𝗽𝗽𝗼𝗿𝘁 𝘂𝘀 𝘁𝗼 𝗱𝗲𝘃𝗲𝗹𝗼𝗽 𝘁𝗵𝗲 𝗯𝗼𝘁 💖✨!"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("RAVANxBOT.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅️ BACK", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(context.bot.first_name)),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_video(
            START_IMG, caption= "<code>°𝗧𝗵𝗲 [𝗭𝗲𝗽𝗵𝘆𝗿](http://t.me/ZephyrManagerBot) 𝗶𝘀 𝗮𝘄𝗮𝗸𝗲 𝘀𝗶𝗻𝗰𝗲✨:</code>: <code>{}</code>".format(
                uptime            
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@run_async
def devx_about_callback(update, context):
    query = update.callback_query
    if query.data == "devx_":
        query.message.edit_text(
            text=""" 𝗜 𝗮𝗺  [𝗭𝗲𝗽𝗵𝘆𝗿](http://t.me/ZephyrManagerBot),𝗮 𝗽𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗴𝗿𝗼𝘂𝗽 𝗺𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗯𝗼𝘁 𝗯𝘂𝗶𝗹𝗱 𝘁𝗼 𝗵𝗲𝗹𝗽 𝘆𝗼𝘂𝗿 𝗺𝗮𝗻𝗮𝗴𝗲 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 𝗲𝗮𝘀𝗶𝗹𝘆.
                 \n❍ I can restrict users.
                 \n❍ I can greet users with customizable welcome messages and even set a group's rules.
                 \n❍ I have an advanced anti-flood system.
                 \n❍ I can warn users until they reach max warns, with each predefined actions such as ban, mute, kick, etc.
                 \n❍ I have a note keeping system, blacklists, and even predetermined replies on certain keywords.
                 \n❍ I check for admins' permissions before executing any command and more stuffs
                 \n\n_DEVX's licensed under the GNU General Public License v3.0_
                 \n❍ Assistant NOT AVAILABELE RIGHT NOW .
                 \nHere is the [💞Repository](https://github.com/Dhruvxbhudev2/YoneRobot).
                 \n\nIf you have any question about bot, let us know at .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="devx_back")
                 ]
                ]
            ),
        )
    elif query.data == "Ravan_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )


@run_async
def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=""" 𝗛𝗶, 𝗶 𝗮𝗺 [𝗭𝗲𝗽𝗵𝘆𝗿](http://t.me/ZephyrManagerBot)
                 \n𝗛𝗲𝗿𝗲 𝗶𝘀 𝘁𝗵𝗲 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗰𝗼𝗱𝗲](https://github.com/Dhruvxbhudev2/YoneRobot) .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Go Back", callback_data="source_back")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 412094015 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@FinalStrikeOp", "𝗔𝗹𝗶𝘃𝗲 💖")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(devx_about_callback, pattern=r"devx_")
    source_callback_handler = CallbackQueryHandler(Source_about_callback, pattern=r"source_")

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
