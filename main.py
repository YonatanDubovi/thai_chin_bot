from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler,
                          Filters, CallbackContext, CallbackQueryHandler)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from data_source import DataSource
import os
# import threading
import logging
import sys

print("Bot started.....")
MODE = os.getenv("MODE")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

TOKEN = os.getenv("TOKEN")
ORDER_NUMBER = 0
CLIENT_NUMBER = ''
SUM_PRICE = 0
DISH_TYPE_KEY_BOARD = [[KeyboardButton("🛒Shopping cart (" + str(SUM_PRICE) + " ₪)")],
                       [KeyboardButton("Appetizer🥟"), KeyboardButton("Soups🍜")],
                       [KeyboardButton("Wok mains🥘"), KeyboardButton("Pad Thai🥡")],
                       [KeyboardButton("side dish🍟"), KeyboardButton("Crispy Chicken🍗")],
                       [KeyboardButton("Noodles🍝"), KeyboardButton("Salads🥗")],
                       [KeyboardButton("Special🥢"), KeyboardButton("Mains from sea🍤")],
                       [KeyboardButton("Sushi🍱"), KeyboardButton("Sushi Sandwich🍣")]]
SELECTED_DISH_NAME = ''
SELECTED_DISH_NUMBER = 0
LIST_OF_DISHES = list()
dataSource = DataSource(os.environ.get("DATABASE_URL"))

if MODE == "dev":
    def run():
        logger.info("Start in DEV mode")
        updater.start_polling()
elif MODE == "prod":
    def run():
        logger.info("Start in PROD mode")
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", "8443")), url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format(os.environ.get("APP_NAME"), TOKEN))
else:
    logger.error("No mode specified!")
    sys.exit(1)


def start_command(update, context):
    """Call start function"""
    buttons = [[KeyboardButton("Order delivery 🛵")], [KeyboardButton("/3 Order and collect myself ☝")],
               [KeyboardButton("/2 Something else  🤷‍♂")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello customer What would you like to do?",
                             reply_markup=ReplyKeyboardMarkup(buttons))


def delivery_handler(update: Update, context: CallbackContext):
    """Request a phone number from the user"""
    con_keyboard = [[KeyboardButton(text="Send my phone number 📲", request_contact=True)]]
    update.message.reply_text("Please share your phone number", reply_markup=ReplyKeyboardMarkup(con_keyboard))


def phone_number_handler(update: Update, context: CallbackContext):
    """Location request for delivery"""
    contact = update.effective_message.contact
    phone_number = "+" + contact.phone_number
    context.user_data["CLIENT_NUMBER"] = phone_number
    #current_sum = context.user_data["SUM"]
    #context.user_data["SUM"] = current_sum + new_VALUE
    dataSource.new_client(phone_number, contact.first_name + " " + contact.last_name)
    loc_keyboard = [[KeyboardButton(text="Send location 📍", request_location=True)]]
    update.message.reply_text("Please share your location for delivery", reply_markup=ReplyKeyboardMarkup(loc_keyboard))


def location_handler(update: Update, context: CallbackContext):
    global ORDER_NUMBER
    global DISH_TYPE_KEY_BOARD
    delivery_phone_number = "+972542562628"
    ORDER_NUMBER = dataSource.get_last_order() + 1
    print(context.user_data["CLIENT_NUMBER"])
    dataSource.new_order(ORDER_NUMBER, '1', context.user_data["CLIENT_NUMBER"], delivery_phone_number)
    dishType_keyboard = DISH_TYPE_KEY_BOARD
    update.message.reply_text(
        "Let's choose dishes to order, you are also welcome to browse the menu: https://thaichin.co.il/menu/#mr-tab-0"
        , reply_markup=ReplyKeyboardMarkup(dishType_keyboard))


def appetizer_handler(update: Update, context: CallbackContext):
    dish_type_handler(update, context, "Appetizer")


def Soups_handles(update: Update, context: CallbackContext):
    dish_type_handler(update, context, "Soups")


def dish_type_handler(update, context, dish_type):
    global LIST_OF_DISHES
    dishes = dataSource.get_dishes(dish_type)
    LIST_OF_DISHES = dishes
    dishes_keyboard = [[KeyboardButton("🔙 Back")]]
    for dish in dishes:
        dishes_keyboard_sub = [KeyboardButton("🥡 "+dish)]
        dishes_keyboard.append(dishes_keyboard_sub)
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=ReplyKeyboardMarkup(dishes_keyboard),
                             text="Select " + dish_type)


def selected_dish_handler(update: Update, context: CallbackContext):
    global SELECTED_DISH_NAME
    SELECTED_DISH_NAME = update.message.text[2:]
    context.bot.sendPhoto(update.message.chat_id, photo=open('test.png', 'rb'))
    buttons = [[InlineKeyboardButton("I don't want this dish ⛔", callback_data='I dont want this dish ⛔')],
               [InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
                InlineKeyboardButton("3", callback_data='3')]]
    replay_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text("How many units would you like of this dish?", reply_markup=replay_markup)


def quantity_handler(update: Update, context: CallbackContext):
    global ORDER_NUMBER
    if get_chosen_dish(context):
        return
    context.user_data["chosen " + SELECTED_DISH_NAME] = "true"
    query = update.callback_query.data
    update.callback_query.answer()
    dish_number = dataSource.get_dish_number(SELECTED_DISH_NAME)
    if "1" in query or "2" in query or "3" in query:
        quantity = int(query)
        dataSource.new_dish_in_order(ORDER_NUMBER, dish_number, quantity)


def get_chosen_dish(context):
    try:
        return context.user_data["chosen " + SELECTED_DISH_NAME]
    except KeyError:
        return None


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler("Back", start_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Order delivery 🛵'), delivery_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.contact, phone_number_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Appetizer🥟'), appetizer_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("Soups🍜"), Soups_handles))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("🥡"), selected_dish_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(quantity_handler))
    run()
