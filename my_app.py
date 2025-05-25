import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from dotenv import load_dotenv
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import ReplyKeyboardRemove


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



async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'option_1':
        await query.edit_message_text("You selected Option 1. Number: 10")
    elif query.data == 'option_2':
        await query.edit_message_text("You selected Option 2. Number: 11")


# # Define command handlers
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # await update.message.reply_text(
#     # "Old keyboard removed. Choose a new option:",
#     # reply_markup=ReplyKeyboardRemove()
#     # )

#     keyboard = [
#         [InlineKeyboardButton("Option 1", callback_data='option_1')],
#         [InlineKeyboardButton("Option 2", callback_data='option_2')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

from db import SessionLocal, TelegramUser

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     telegram_id = str(update.effective_user.id)
#     # print("***********")
#     # print(f"Received /start command from user: {telegram_id}")
#     # print("***********")
#     # DB session
#     db = SessionLocal()
#     user = db.query(TelegramUser).filter_by(telegram_user_id=telegram_id).first()

#     if user:
#         # Authorized user
#         await update.message.reply_text("✅ You are authorized.")
        
#         # Show menu
#         keyboard = [
#             [InlineKeyboardButton("Option 1", callback_data='option_1')],
#             [InlineKeyboardButton("Option 2", callback_data='option_2')]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
#     else:
#         # Unauthorized user
#         await update.message.reply_text("❌ You are not authorized to use this bot.")
    
#     db.close()

import pyodbc

# def get_categories_for_sazman(sazman_id):
#     try:
#         conn = pyodbc.connect(
#             'DRIVER={ODBC Driver 17 for SQL Server};'
#             'SERVER=your_sql_server_host,1433;'
#             'DATABASE=your_database_name;'
#             'UID=your_username;'
#             'PWD=your_password'
#         )
#         cursor = conn.cursor()

#         query = f"SELECT * FROM category WHERE sazmanid = ? ORDER BY [order]"
#         cursor.execute(query, sazman_id)
#         rows = cursor.fetchall()

#         # Optional: parse rows into a list of dicts
#         columns = [column[0] for column in cursor.description]
#         results = [dict(zip(columns, row)) for row in rows]

#         cursor.close()
#         conn.close()

#         return results
#     except Exception as e:
#         print(f"❌ SQL Server error: {e}")
#         return None


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     telegram_id = str(update.effective_user.id)
#     print("***********")
#     print(f"Received /start command from user: {telegram_id}")
#     print("***********")
#     # DB session
#     db = SessionLocal()
#     user = db.query(TelegramUser).filter_by(telegram_user_id=telegram_id).first()

#     if user:
#         # Authorized user
#         await update.message.reply_text("✅ You are authorized.")
        
#         # Show menu
#         keyboard = [
#             [InlineKeyboardButton("Option 1", callback_data='option_1')],
#             [InlineKeyboardButton("Option 2", callback_data='option_2')]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
#     else:
#         # Unauthorized user
#         await update.message.reply_text("❌ You are not authorized to use this bot.")
    
#     db.close()

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from db import SessionLocal, TelegramUser
from db_mssql import get_sqlserver_connection  # From earlier step
import logging

logger = logging.getLogger(__name__)


# 1. Check if Telegram user is authorized
def is_user_authorized(telegram_id: str) -> int | None:
    db: Session = SessionLocal()
    try:
        user = db.query(TelegramUser).filter_by(telegram_user_id=telegram_id).first()
        return user.sazman_id if user else None
    finally:
        db.close()


# 2. Query categories from SQL Server
def get_categories_by_sazman_id(sazman_id: int):
    try:
        conn = get_sqlserver_connection()
        # print(f" ---- Connected to SQL Server for Sazman ID: {sazman_id}")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category WHERE sazmanid = ? ORDER BY [order]", sazman_id)
        temp = cursor.fetchall()
        return temp
    except Exception as e:
        logger.error(f"SQL Server error: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()
            
# 2. Query categories from SQL Server
def get_sazman_title_from_sazman_id(sazman_id: int):
    try:
        conn = get_sqlserver_connection()
        # print(f" ---- Connected to SQL Server for Sazman ID: {sazman_id}")
        cursor = conn.cursor()
        cursor.execute("SELECT Tittle FROM [DashboardbManager].[dbo].[Sazman] WHERE id=?", sazman_id)
        temp = cursor.fetchall()
        if temp:
            return temp[0][0]
        else:
            logger.warning(f"No Sazman found with ID: {sazman_id}")
            return 'یافت نشد'
    except Exception as e:
        logger.error(f"SQL Server error: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_category_response(rows):
    if not rows:
        return "ℹ️ No categories found for this Sazman ID.", None

    # Each category becomes a button
    keyboard = [
        [InlineKeyboardButton(text=row.Name, callback_data=f"category_{row.Id}")]
        for row in rows
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return "📂 لطفا یک دسته بندی را انتخاب کنید:", reply_markup


# 4. Send main keyboard (option 1 / 2)
async def send_main_keyboard(update: Update):
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='option_1')],
        [InlineKeyboardButton("Option 2", callback_data='option_2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    sazman_id = is_user_authorized(telegram_id)

    if sazman_id:
        # get sazman title from SQL Server
        sazman_title = get_sazman_title_from_sazman_id(sazman_id)
        await update.message.reply_text(f"✅ دسترسی شما تایید شد. سازمان شما: {sazman_title}")

        rows = get_categories_by_sazman_id(sazman_id)

        if rows is not None:
            text, reply_markup = build_category_response(rows)
            await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ خطا در گرفتن دسته بندی ها از دیتابیس.")
    else:
        await update.message.reply_text(
            f"❌ شما اجازه دسترسی به این ربات را ندارید. لطفاً با مدیر تماس بگیرید.\n\n"
            f"آیدی تلگرام جهت تعریف: <code>{telegram_id}</code>",
            parse_mode='HTML'
        )




 
from telegram.ext import CallbackQueryHandler

# def get_pages_by_category_id(category_id):
#     print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
#     try:
#         conn = get_sqlserver_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM [DashboardbManager].[dbo].[Page] where CategoryId = ?", category_id)
#         # cursor.execute("SELECT Id, Title FROM dbo.Page WHERE CategoryId = ?", category_id)
#         rows = cursor.fetchall()
#         return rows
#     except Exception as e:
#         print("❌ SQL Error:", e)
#         return []
def get_pages_by_category_id(category_id: int):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
    try:
        conn = get_sqlserver_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Title FROM Page WHERE CategoryId = ?", category_id)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"SQL Server error while fetching pages: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def build_page_response(rows):
    if not rows:
        return "ℹ️ No pages found for this category.", None

    keyboard = [
        [InlineKeyboardButton(text=row.Title, callback_data=f"page_{row.Id}")]
        for row in rows
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return "📄 لطفا یک صفحه را انتخاب کنید:", reply_markup

async def handle_category_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ handle_category_click triggered!")  # Debug print
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split("_")[1])
    print(f"➡️ Category ID: {category_id}")

    pages = get_pages_by_category_id(category_id)
    print(f"Fetched {len(pages)} pages") if pages else print("No pages found")

    text, reply_markup = build_page_response(pages)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


# async def handle_category_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("************** handle_category_click ******************")
#     query = update.callback_query
#     await query.answer()

#     # Step 1: Extract Category ID from callback_data
#     callback_data = query.data  # e.g., 'category_4'
#     category_id = int(callback_data.split("_")[1])

#     # Step 2: Query database for pages under this category
#     pages = get_pages_by_category_id(category_id)

#     # Step 3: Format response
#     if pages:
#         text = "📄 Pages in this category:\n" + "\n".join(f"- {page.Title}" for page in pages)
#     else:
#         text = "ℹ️ No pages found for this category."

#     # Step 4: Respond in the chat (you can use edit or send a new message)
#     await query.edit_message_text(text)

# async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logger.info(f"/test from {update.effective_user.username}")
#     await update.message.reply_text("Hello! This is a test message.")

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

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_text = update.message.text
#     logger.info(f"Received from {update.effective_user.username}: {user_text}")

#     # Show 'typing...' while processing
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

#     try:
#         # Send user message to AI
#         response = ai_client.complete(
#             messages=[UserMessage(user_text)],
#             temperature=0.5,
#             top_p=0.95,
#             max_tokens=1500,
#             model=MODEL_NAME,
#         )
#         ai_reply = response.choices[0].message.content
#     except Exception as e:
#         logger.error(f"AI API error: {e}")
#         ai_reply = "Sorry, something went wrong with the AI."

#     await update.message.reply_text(ai_reply)


from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
import pandas as pd
import io
import logging

# Assuming ai_client and MODEL_NAME are already defined and initialized

# async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     document = update.message.document
#     file_name = document.file_name
#     mime_type = document.mime_type
#     logger.info(f"Received document: {file_name} with MIME type: {mime_type}")

#     # Indicate bot is processing
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

#     try:
#         # Download the file
#         file = await context.bot.get_file(document.file_id)
#         file_bytes = await file.download_as_bytearray()

#         # Read the file into a DataFrame
#         if mime_type == 'text/csv' or file_name.endswith('.csv'):
#             df = pd.read_csv(io.BytesIO(file_bytes))
#         elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] or file_name.endswith(('.xls', '.xlsx')):
#             df = pd.read_excel(io.BytesIO(file_bytes))
#         else:
#             await update.message.reply_text("Unsupported file type. Please upload a CSV or Excel file.")
#             return

#         # Convert DataFrame to string
#         data_str = df.to_string()

#         # Send data to AI for explanation
#         response = ai_client.complete(
#             messages=[UserMessage(f"Explain this data:\n{data_str}")],
#             temperature=0.5,
#             top_p=0.95,
#             max_tokens=1500,
#             model=MODEL_NAME,
#         )
#         ai_reply = response.choices[0].message.content

#         # Send AI response back to user
#         await update.message.reply_text(ai_reply)

#     except Exception as e:
#         logger.error(f"Error processing document: {e}")
#         await update.message.reply_text("An error occurred while processing the file.")

# Add handlers to bot_app
# bot_app.add_handler(CommandHandler("start", start))
# bot_app.add_handler(CommandHandler('start', start))
# bot_app.add_handler(CallbackQueryHandler(handle_menu_choice))

from telegram.ext import CallbackQueryHandler



bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_category_click, pattern=r'^category_\d+$'))




async def debug_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print("Callback data received:", query.data)
    await query.answer("debug")

bot_app.add_handler(CallbackQueryHandler(debug_all_callbacks))  # Add this temporarily to catch all callback data


# bot_app.add_handler(CommandHandler("test", test))
# bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
# bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))


# Ensure bot is initialized only once
bot_initialized = False
loop = asyncio.get_event_loop()

# Telegram webhook route
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    # logger.info(f"Received update: {update_data}")
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

