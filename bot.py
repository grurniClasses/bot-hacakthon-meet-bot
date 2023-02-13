import logging
import random
import string
import bot_settings
from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
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

WELCOME_MESSAGE = "Hey there! \bChoose date options to organize your meeting \b let me know you are done by sending /end"
meetings_message = f'Please select the dates you can from the following dates : '

def start(update: Update, context: CallbackContext):
    context.user_data["dates"] = {}
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        code = update.message.text.split()[1]
        data = meetings.find_one({'code': code})
        context.user_data['code'] = code
        options_list = list(data["dates"].keys())
        button_options_list = [
            [InlineKeyboardButton(f"{option}", callback_data=f"option:{option}")]  for option in options_list
        ]
        buttons = button_options_list
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=chat_id, text=meetings_message, reply_markup = reply_markup)
    else:
        calendar_handler(update,context)

def get_random_code(k=16):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))

def calendar_handler(update: Update, context: CallbackContext):
    update.message.reply_text(WELCOME_MESSAGE,
                        reply_markup=telegramcalendar.create_calendar())
def callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    logger.info(f"> CALLBACK #{chat_id}, {data=}")
    query.answer()
    cmd = data.split(":")[0]
    if cmd == "option":
        chosen_dates = [data.split(":")[1]]
        query.edit_message_text(text=f"your chosen dates are: {chosen_dates}")
        dates = meetings.find_one({'code': context.user_data['code']})["dates"]
        for date in chosen_dates:
            dates[date] += 1
        meetings.update_one({'code': context.user_data['code']}, {"$set": {'dates': dates}})
    #todo Keep buttons on and update chosen dates
    print(data)
    cmd = data.split(";")
    if cmd[0] == "DAY" or cmd[0]=='NEXT-MONTH':
        selected, date = telegramcalendar.process_calendar_selection(update, context)
        if selected:
            print(date)
            date = date.strftime("%d/%m/%Y")
            d = context.user_data.get("dates", {})
            d[date] = d.get(date, 0) + 1
            context.user_data["dates"] = d
            context.bot.send_message(chat_id=update.callback_query.from_user.id,text="You selected %s" % (date))
            query.edit_message_text(text=meetings_message, reply_markup=telegramcalendar.create_calendar())

def status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    dates = meetings.find_one({'code': context.user_data['code']})["dates"]
    context.bot.send_message(chat_id=chat_id, text="Your guests chose:")

    for k, v in dates.items():
        thumbs = (v-1)*"👍"
        context.bot.send_message(chat_id=chat_id, text=f"{k}: {thumbs}")

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
    context.bot.send_message(chat_id=chat_id, text='Please forward the following message to your guests')
    meeting_message = f'You are invited by {update.message.chat.first_name} to a meeting. \b Follow the link to see the invitation {url_req} and press *START*'
    context.bot.send_message(chat_id=chat_id, text=meeting_message)

    context.bot.send_message(chat_id=chat_id, text='Give them a little while to answer. send /status to see what they chose')



my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(CommandHandler("status", status))
my_bot.dispatcher.add_handler(CommandHandler("end", end))
my_bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))


logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")
