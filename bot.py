import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    Updater
)
from pymongo import MongoClient

import bot_settings

client = MongoClient()
db = client.get_database("meetingDB")
meetings = db.get_collection("meetings")
meeting = {
    'meeting_id':"",
    'dates': "2"
}




logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "Hey there! when do you want to organize your meeting?"
MEETING_HOST = "marina"
MEETING_MESSAGE = f'you are invited by {MEETING_HOST} to a meeting. {MEETING_HOST} has chosen this dates for the meeting {meeting["dates"]}'

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        meeting_id = update.message.text.split()[1]
        print(meeting)
        context.bot.send_message(chat_id=chat_id, text=MEETING_MESSAGE)
        meetings.find()

    else:
        context.bot.send_message(chat_id=chat_id, text=WELCOME_MESSAGE)



def respond(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Just a second...",)
    logger.info(f"= Got on chat #{chat_id}")
    user_dates = update.message.text.split(",")
    meeting["dates"] = user_dates
    meeting['meeting_id'] = chat_id
    meetings.insert_one(meeting)
    print(meeting)







my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(MessageHandler(Filters.text, respond))

logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")