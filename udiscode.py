import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    Updater, CallbackQueryHandler,
)

import bot_settings

WELCOME_TEXT = "hit /yesno for yes no or /number for number"

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT)


def info(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    x = context.user_data.get("x", 0) + 1
    logger.info(f"> INFO #{chat_id}, {x=}")
    context.user_data["x"] = x
    context.bot.send_message(chat_id=chat_id, text=f'INFO: {x}')


def counters(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> CHOOSE NUMBER Started on chat #{chat_id}")

    d = context.user_data.get("counters", {})
    reply_markup = get_counters_keyboard(d)
    context.bot.send_message(chat_id=chat_id, text="Choose number", reply_markup=reply_markup)


def get_counters_keyboard(d):
    button_list = [
        InlineKeyboardButton(f"{i} ({d.get(i, 0)})", callback_data=f"counters:{i}") for i in range(1, 10)
    ]
    buttons = [button_list[:3], button_list[3:6], button_list[6:9]]
    reply_markup = InlineKeyboardMarkup(buttons)
    return reply_markup


def callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    logger.info(f"> CALLBACK #{chat_id}, {data=}")
    query.answer()
    print(data)
    cmd = data.split(":")[0]
    if cmd == "counters":
        n = int(data.split(":")[1])
        d = context.user_data.get("counters", {})
        d[n] = d.get(n, 0) + 1
        context.user_data["counters"] = d
        reply_markup = get_counters_keyboard(d)
        query.edit_message_text(text=f"{data}", reply_markup=reply_markup)


my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(CommandHandler("info", info))
my_bot.dispatcher.add_handler(CommandHandler("number", counters))
my_bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

logger.info("* Start polling...")
my_bot.start_polling(poll_interval=3)  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")