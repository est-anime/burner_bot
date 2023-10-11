import telegram
from telegram.ext import Updater, MessageHandler, Filters

# Replace 'YOUR_BOT_TOKEN' with your actual bot token.
bot = telegram.Bot(token='YOUR_BOT_TOKEN')

def handle_message(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text
    # Handle user messages here

updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
