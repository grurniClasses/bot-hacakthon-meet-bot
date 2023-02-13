import logging
import random
import string
from pprint import pprint
import bot_settings

from telegram import  ReplyKeyboardRemove



from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    Updater, CallbackQueryHandler
)
from pymongo import MongoClient

import telegramcalendar

bot_name = 'HebrewguessnumberBOT'
client = MongoClient()
db = client.get_database("meetingDB")
meetings = db.get_collection("meetings")

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "Hey there! when do you want to organize your meeting?"


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        code = update.message.text.split()[1]
        data = meetings.find_one({'code': code})
        meetings_message = f'Please select the dates you can from the flows dates : {data["dates"]}'
        context.bot.send_message(chat_id=chat_id, text=meetings_message)
        context.user_data['code']=code
    else:
        context.bot.send_message(chat_id=chat_id, text=WELCOME_MESSAGE)

def get_random_code(k=16):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


def calendar_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please select a date: ",
                        reply_markup=telegramcalendar.create_calendar())

def inline_handler(update: Update, context: CallbackContext):
    selected,date = telegramcalendar.process_calendar_selection(update, context)
    if selected:
        context.bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="You selected %s" % (date.strftime("%d/%m/%Y")),
                        reply_markup=ReplyKeyboardRemove())


def respond(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    code = get_random_code()
    logger.info(f"= Got on chat #{chat_id},{code=}")
    meeting = {
        'dates': update.message.text.split(','),
        'createre_chat_id': chat_id,
        'code':code
    }
    result = meetings.insert_one(meeting)
    url_req = f"https://t.me/{bot_name}?start={code}"
    context.bot.send_message(chat_id=chat_id, text='Please forward the follow message to your guests')
    meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req}'
    context.bot.send_message(chat_id=chat_id, text=meeting_message)


my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(CommandHandler("calendar", calendar_handler))
my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_handler))
my_bot.dispatcher.add_handler(MessageHandler(Filters.text, respond))



logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")
