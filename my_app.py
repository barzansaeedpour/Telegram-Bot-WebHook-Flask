import os
import logging
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app and bot app
bot_app = Application.builder().token(TOKEN).build()

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start from {update.effective_user.username}")
    await update.message.reply_text("Hello! Webhook is working!")

# Command handler for /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/test from {update.effective_user.username}")
    await update.message.reply_text("Hello! This is a test message.")

# Add command handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("test", test))

# Ensure Application is initialized only once
app_initialized = False

async def init_bot():
    global app_initialized
    if not app_initialized:
        logger.info("Initializing bot Application...")
        await bot_app.initialize()
        await bot_app.start()  # Ensure background tasks start
        app_initialized = True

# Webhook endpoint to receive updates from Telegram
async def webhook(request):
    update_data = await request.json()
    logger.info(f"Received update: {update_data}")
    update = Update.de_json(update_data, bot_app.bot)
    await bot_app.process_update(update)
    return web.Response(text="OK")

# Health check endpoint
async def index(request):
    return web.Response(text="Bot is running.")

# Create aiohttp app and add routes
app = web.Application()
app.router.add_post(f"/webhook/{TOKEN}", webhook)
app.router.add_get("/", index)

# Start aiohttp app
if __name__ == "__main__":
    logger.info("Starting aiohttp app...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_bot())
    web.run_app(app, port=9090)
