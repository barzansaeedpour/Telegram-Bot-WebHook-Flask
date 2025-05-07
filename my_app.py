import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot app
bot_app = Application.builder().token(TOKEN).build()

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start from {update.effective_user.username}")
    await update.message.reply_text("Hello! Webhook is working!")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/test from {update.effective_user.username}")
    await update.message.reply_text("Hello! This is a test message.")

import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential
# Load model name and token
AI_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")

# Initialize AI client
ai_client = ChatCompletionsClient(
    endpoint="https://models.github.ai/inference",
    credential=AzureKeyCredential(AI_TOKEN),
)

from telegram.constants import ChatAction  # Needed for 'typing'

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Received from {update.effective_user.username}: {user_text}")

    # Show 'typing...' while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # Send user message to AI
        response = ai_client.complete(
            messages=[UserMessage(user_text)],
            temperature=0.5,
            top_p=0.95,
            max_tokens=1500,
            model=MODEL_NAME,
        )
        ai_reply = response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI API error: {e}")
        ai_reply = "Sorry, something went wrong with the AI."

    await update.message.reply_text(ai_reply)



# Add handlers to bot_app
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("test", test))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Ensure bot is initialized only once
bot_initialized = False
loop = asyncio.get_event_loop()

# Telegram webhook route
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    logger.info(f"Received update: {update_data}")
    update = Update.de_json(update_data, bot_app.bot)
    loop.run_until_complete(bot_app.process_update(update))
    return "OK", 200


# Health check route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running.2", 200

from waitress import serve

if __name__ == "__main__":
    
    # Initialize bot before starting the server
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.start())

    print("Starting server with Waitress...")
    serve(app, host="0.0.0.0", port=9090)

