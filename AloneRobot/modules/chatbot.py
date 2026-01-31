import html
import json
import re
from time import sleep
import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import AloneRobot.modules.sql.chatbot_sql as sql
from AloneRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher,CHATBOT_API
from AloneRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from AloneRobot.modules.log_channel import gloggable
from urllib.parse import quote_plus


@user_admin_no_reply
@gloggable
def alonerm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_alone = sql.set_alone(chat.id)
        if is_alone:
            is_alone = sql.set_alone(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ᴀɪ ᴅɪꜱᴀʙʟᴇᴅ\n"
                f"<b>ᴀᴅᴍɪɴ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin_no_reply
@gloggable
def aloneadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_alone = sql.rem_alone(chat.id)
        if is_alone:
            is_alone = sql.rem_alone(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ᴀɪ ᴇɴᴀʙʟᴇ\n"
                f"<b>ᴀᴅᴍɪɴ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@gloggable
def alone(update: Update, context: CallbackContext):
    message = update.effective_message
    msg = "• ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="add_chat({})"),
                InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="rm_chat({})"),
            ],
        ]
    )
    message.reply_text(
        text=msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def alone_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "alone":
        return True
    elif BOT_USERNAME in message.text.upper():
        return True
    elif reply_message:
        if reply_message.from_user.id == BOT_ID:
            return True
    else:
        return False


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_alone = sql.is_alone(chat_id)
    if is_alone:
        return

    if message.text and not message.document:
        if not alone_message(context, message):
            return
        bot.send_chat_action(chat_id, action="typing")
        from urllib.parse import quote_plus

def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot

    is_alone = sql.is_alone(chat_id)
    if is_alone:
        return

    if not message.text or message.document:
        return

    if not alone_message(context, message):
        return

    bot.send_chat_action(chat_id, action="typing")

    text = quote_plus(message.text)

    url = (
        "http://api.acix.site"
        f"?apikey=FREEAPIKEY&message={text}"
    )

    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        print("REQUEST ERROR:", e)
        message.reply_text("❌ Chatbot service unreachable.")
        return

    if response.status_code != 200:
        print("API STATUS:", response.status_code)
        print("API TEXT:", response.text)
        message.reply_text("⚠️ Chatbot API error.")
        return

    try:
        out = response.json()
    except Exception as e:
        print("JSON ERROR:", e)
        print("RAW RESPONSE:", response.text)
        message.reply_text("⚠️ Invalid chatbot response.")
        return

    reply = out.get("reply")
    if not reply:
        message.reply_text("🤖 I didn't understand that.")
        return

    message.reply_text(reply)









CHATBOTK_HANDLER = CommandHandler("chatbot", alone, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(aloneadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(alonerm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    CHATBOT_HANDLER,
]
