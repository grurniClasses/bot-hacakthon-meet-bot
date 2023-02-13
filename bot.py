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

client = MongoClient()
db = client.get_database("meetingDB")
meetings = db.get_collection("meetings")

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "Hey there! \bwhen do you want to organize your meeting?"

def start(update: Update, context: CallbackContext):
    context.user_data["dates"] = {}
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        code = update.message.text.split()[1]
        data = meetings.find_one({'code': code})
        meetings_message = f'Please select the dates you can from the flows dates : {data["dates"]}'
        context.bot.send_message(chat_id=chat_id, text=meetings_message)
    else:
        calendar_handler(update,context)

def get_random_code(k=16):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


def calendar_handler(update: Update, context: CallbackContext):
    update.message.reply_text(text=WELCOME_MESSAGE,reply_markup=telegramcalendar.create_calendar())

# def inline_handler(update: Update, context: CallbackContext):
#     selected,date = telegramcalendar.process_calendar_selection(update, context)
#     if selected:
#         context.bot.send_message(chat_id=update.callback_query.from_user.id,
#                         text="You selected %s" % (date.strftime("%d/%m/%Y")),
#                         reply_markup=ReplyKeyboardRemove())
#         chat_id = update.effective_chat.id
#         code = get_random_code()
#         logger.info(f"= Got on chat #{chat_id},{code=}")
#         datesDic={}
#         datesDic[date.strftime("%d/%m/%Y")] = 1
#         meeting = {
#             'dates': datesDic,
#             'createre_chat_id': chat_id,
#             'code': code
#         }
#         pprint(meeting)
#         result = meetings.insert_one(meeting)
#         url_req = f"https://t.me/{bot_settings.BOT_NAME}?start={code}"
#         context.bot.send_message(chat_id=chat_id, text='Please forward the follow message to your guests')
#         meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req}'
#         context.bot.send_message(chat_id=chat_id, text=meeting_message)

# def respond(update: Update, context: CallbackContext,date=None):
#     if context.user_data.get('code') is None:
#         chat_id = update.effective_chat.id
#         code = get_random_code()
#         logger.info(f"= Got on chat #{chat_id},{code=}")
#         datesDic = {}
#         for date in update.message.text.split(','):
#             datesDic[date] = 1
#         meeting = {
#             'dates': datesDic,
#             'createre_chat_id': chat_id,
#             'code':code
#         }
#         result = meetings.insert_one(meeting)
#         url_req = f"https://t.me/{bot_settings.BOT_NAME}?start={code}"
#         context.bot.send_message(chat_id=chat_id, text='Please forward the follow message to your guests')
#         meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req}'
#         context.bot.send_message(chat_id=chat_id, text=meeting_message)
#     else:
#         dates = meetings.find_one({'code': context.user_data['code']})["dates"]
#         for date in update.message.text.split(','):
#             dates[date] += 1
#         meetings.update_one({'code':context.user_data['code']},{"$set":{'dates':dates}})

def status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    dates = meetings.find_one({'code': context.user_data['code']})["dates"]
    context.bot.send_message(chat_id=chat_id, text=dates)

def callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    logger.info(f"> CALLBACK #{chat_id}, {data=}")
    query.answer()
    cmd = data.split(";")
    if cmd[0] == "DAY":
        date = f'{cmd[3]}/{cmd[2]}/{cmd[1]}'
        d = context.user_data.get("dates", {})
        d[date] = d.get(date, 0) + 1
        context.user_data["dates"] =d
        query.edit_message_text(text=f"{data}", reply_markup=telegramcalendar.create_calendar())
        context.bot.send_message(chat_id=update.callback_query.from_user.id,
                                 text="You selected %s" % (date))

def end(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    code = get_random_code()
    logger.info(f"= Got on chat #{chat_id},{code=}")
    meeting = {
        'dates': context.user_data["dates"],
        'createre_chat_id': chat_id,
        'code':code
    }
    result = meetings.insert_one(meeting)
    url_req = f"https://t.me/{bot_settings.BOT_NAME}?start={code}"
    context.bot.send_message(chat_id=chat_id, text='Please forward the follow message to your guests')
    meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req}'
    context.bot.send_message(chat_id=chat_id, text=meeting_message)


my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(CommandHandler("status", status))
my_bot.dispatcher.add_handler(CommandHandler("end", end))
my_bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

# my_bot.dispatcher.add_handler(CommandHandler("calendar", calendar_handler))
# my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_handler))
# my_bot.dispatcher.add_handler(MessageHandler(Filters.text, respond))



logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")
