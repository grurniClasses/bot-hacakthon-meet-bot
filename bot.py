import logging
from pprint import pprint

from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    Updater
)
from pymongo import MongoClient

import bot_settings
bot_name = 'GiliTheKingBot'
client = MongoClient()
db = client.get_database("meetingDB")
meetings = db.get_collection("meetings")

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "Hey there! when do you want to organize your meeting?"
MEETING_HOST = "marina"
# MEETING_MESSAGE = f'you are invited by {MEETING_HOST} to a meeting. {MEETING_HOST} has chosen this dates for the meeting {meeting["dates"]}'

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        meeting_id = update.message.text.split()[1]
        # print(meeting)
        # context.bot.send_message(chat_id=chat_id, text=MEETING_MESSAGE)
        meetings.find()

    else:
        context.bot.send_message(chat_id=chat_id, text=WELCOME_MESSAGE)



def respond(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"= Got on chat #{chat_id}")
    meeting={
        'dates':update.message.text.split(','),
        'meeting_id':chat_id
    }
    result = meetings.insert_one(meeting)
    url_req = f"https://t.me/{bot_name}?start={result.inserted_id}"
    context.bot.send_message(chat_id=chat_id, text='Please forward the follow message to your guests')
    meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req}'
    context.bot.send_message(chat_id=chat_id, text=meeting_message)

my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(MessageHandler(Filters.text, respond))

logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")