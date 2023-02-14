import logging
import random
import string
import bot_settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
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

WELCOME_INVITER_MESSAGE = "Hey there! \nChoose date options to organize your meeting \nLet me know you are done by sending /end or pressing the submit button"
SUBMIT_BUTTON = 'Let me know when you are done by pressing the submit button'
GUEST_MESSAGE = 'Please select the dates you can from the following dates : '


def get_random_code(k=16):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


def start(update: Update, context: CallbackContext):
    context.user_data["dates"] = []
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    if len(update.message.text.split()) > 1:
        context.user_data['code'] = update.message.text.split()[1]
        guesses = meetings.find_one({'code': context.user_data['code']})['guesses']
        if chat_id in guesses:
            context.bot.send_message(chat_id=chat_id, text='Sorry, but you already register for the meeting')
        else:
            guess_schedule_handler(update, context)
    else:
        calendar_handler(update, context)


def create_option_button(context: CallbackContext):
    code = context.user_data['code']
    dates = context.user_data['dates']
    data = meetings.find_one({'code': code})
    options_list = data["dates"]
    button_options_list = [
        [InlineKeyboardButton(f"{option} {'✔' if option in dates else ' '}", callback_data=f"option:{option}")] for
        option in
        options_list
    ]
    reply_markup = InlineKeyboardMarkup(button_options_list)
    return reply_markup


def guess_schedule_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text(GUEST_MESSAGE, reply_markup=create_option_button(context))
    submit_button = [
        [InlineKeyboardButton("Submit", callback_data="guess_submit")]
    ]
    reply_markup = InlineKeyboardMarkup(submit_button)
    context.bot.send_message(chat_id=chat_id, text=SUBMIT_BUTTON, reply_markup=reply_markup)


def calendar_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text(WELCOME_INVITER_MESSAGE,
                              reply_markup=telegramcalendar.create_calendar(context.user_data["dates"]))
    submit_button = [
        [InlineKeyboardButton("Submit", callback_data="inviter_submit")]
    ]
    reply_markup = InlineKeyboardMarkup(submit_button)
    context.bot.send_message(chat_id=chat_id, text=SUBMIT_BUTTON, reply_markup=reply_markup)


def callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    logger.info(f"> CALLBACK #{chat_id}, {data=}")
    query.answer()
    cmd = data.split(":")[0]
    if cmd == "option":
        update_guess_dates(update, context)
    cmd = data.split(";")
    if cmd[0] == "DAY" or cmd[0] == 'NEXT-MONTH' or cmd[0] == 'PREV-MONTH':
        update_inviter_dates(update, context)
    if cmd[0] == 'inviter_submit':
        inviter_submit(update, context, query.message.chat.first_name)
    if cmd[0] == 'guess_submit':
        guess_submit(update, context)


def update_guess_dates(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = query.from_user.id
    chosen_dates = data.split(":")[1]
    li = context.user_data.get("dates")
    if chosen_dates not in li:
        li.append(chosen_dates)
        context.user_data["dates"] = li
    else:
        li.remove(chosen_dates)
    query.edit_message_text(text=GUEST_MESSAGE, reply_markup=create_option_button(context))


def update_inviter_dates(update: Update, context: CallbackContext):
    query = update.callback_query
    selected, date = telegramcalendar.process_calendar_selection(context.user_data["dates"], update, context)
    if selected:
        date = date.strftime("%d/%m/%Y")
        li = context.user_data.get("dates")
        if date not in li:
            li.append(date)
            context.user_data["dates"] = li
        else:
            li.remove(date)
        query.edit_message_text(text=WELCOME_INVITER_MESSAGE,
                                reply_markup=telegramcalendar.create_calendar(context.user_data["dates"]))


def status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    dates = meetings.find_one({'code': context.user_data['code']})["dates"]
    guesses = meetings.find_one({'code': context.user_data['code']})["guesses"]
    context.bot.send_message(chat_id=chat_id, text=f"Your guests chose: ({len(guesses)} answered)")
    for k, v in dates.items():
        thumbs = v * "👍"
        context.bot.send_message(chat_id=chat_id, text=f"{k}: {thumbs}")


def inviter_submit(update: Update, context: CallbackContext, name=None):
    if name == None:
        name = update.message.chat.first_name
    chat_id = update.effective_chat.id
    code = get_random_code()
    logger.info(f"= Got on chat #{chat_id},{code=}")
    dic = {}
    for date in context.user_data["dates"]:
        dic[date] = 0
    meeting = {
        'dates': dic,
        'code': code,
        'guesses': []
    }
    meetings.insert_one(meeting)
    url_req = f"https://t.me/{bot_settings.BOT_NAME}?start={code}"
    update.callback_query.edit_message_text(text='Please forward the following message to your guests')
    meeting_message = f'You are invited by {name} to a meeting. \nFollow the link to see the invitation {url_req} and press *START*'
    context.bot.send_message(chat_id=chat_id, text=meeting_message, parse_mode=ParseMode.MARKDOWN)
    context.bot.send_message(chat_id=chat_id,
                             text='Give them a little while to answer. Send /status to see what they chose')

def guess_submit(update: Update, context: CallbackContext):
    dates = meetings.find_one({'code': context.user_data['code']})["dates"]
    for date in context.user_data["dates"]:
        dates[date] += 1
    meetings.update_one({'code': context.user_data['code']}, {"$set": {'dates': dates}})
    meetings.update_one({'code': context.user_data['code']}, {'$push': {'guesses': update.effective_chat.id}})
    update.callback_query.edit_message_text("Your answers been submitted. \nSend /status to see the other answers")


my_bot = Updater(token=bot_settings.BOT_TOKEN, use_context=True)
my_bot.dispatcher.add_handler(CommandHandler("start", start))
my_bot.dispatcher.add_handler(CommandHandler("status", status))
my_bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

logger.info("* Start polling...")
my_bot.start_polling()  # Starts polling in a background thread.
my_bot.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")
