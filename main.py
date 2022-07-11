from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler,
                          Filters, CallbackContext, CallbackQueryHandler)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from data_source import DataSource
import os
#import threading
#import time
#import datetime
#import logging
#import sys

print("Bot started.....")

TOKEN = os.getenv("TOKEN")
dataSource = DataSource(os.environ.get("DATABASE_URL"))

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
    loc_keyboard = [[KeyboardButton(text="Send location 📍", request_location=True)]]
    update.message.reply_text("Please share your location for delivery", reply_markup=ReplyKeyboardMarkup(loc_keyboard))


def location_handler(update: Update, context: CallbackContext):
    dishType_keyboard = [[KeyboardButton("Appetizer🥟"), KeyboardButton("Soups🍜")],[KeyboardButton("Wok mains🥘"), KeyboardButton("Pad Thai🥡")],
                         [KeyboardButton("side dish🍟"), KeyboardButton("Crispy Chicken🍗")],
                         [KeyboardButton("Noodles🍝"), KeyboardButton("Salads🥗")],
                         [KeyboardButton("Special🥢"), KeyboardButton("Mains from sea🍤")],
                         [KeyboardButton("Sushi🍱"), KeyboardButton("Sushi Sandwich🍣")]]
    update.message.reply_text("Let's choose dishes to order, you are also welcome to browse the menu: https://thaichin.co.il/menu/#mr-tab-0"
                              , reply_markup=ReplyKeyboardMarkup(dishType_keyboard))

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler("Back", start_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Order delivery 🛵'), delivery_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.contact, phone_number_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    dataSource.create_tables()
    updater.start_polling()
    updater.idle()
