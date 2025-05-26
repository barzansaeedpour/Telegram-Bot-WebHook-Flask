import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
from waitress import serve
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Flask app
app = Flask(__name__)

# Initialize the Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# Define command handler
async def start(update: Update, context):
    await update.message.reply_text("Hello from Flask + Telegram Bot!")

# Add handler to the application
application.add_handler(CommandHandler("start", start))

# Define route for webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(await request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# Define route for health check
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    print("Starting server with Waitress on http://127.0.0.1:9000")
    # Set webhook
    asyncio.run(application.bot.set_webhook(f"{WEBHOOK_URL}/webhook"))
    # Start Flask app with Waitress
    serve(app, host="0.0.0.0", port=9000)
