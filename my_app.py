from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")



bot = Bot(token=TOKEN)

app = Flask(__name__)

# Dispatcher for handling updates
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

# Command handler
def start(update, context):
    update.message.reply_text("Hello! This is a webhook-based bot.")

dispatcher.add_handler(CommandHandler("start", start))

# Webhook route
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Optional health check route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

if __name__ == "__main__":
    # For development: use flask directly
    app.run(port=8443)
