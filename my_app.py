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
from db import SessionLocal, TelegramUser
import pyodbc
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from db import SessionLocal, TelegramUser
from db_mssql import get_sqlserver_connection  # From earlier step
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from db import SessionLocal, DashboardPageConnection   
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential
from telegram.constants import ChatAction  # Needed for 'typing'
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
import pandas as pd
import io
import logging
from telegram.ext import CallbackQueryHandler
from waitress import serve

# Load environment variables
load_dotenv()

# Load model name and token
AI_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")

# Initialize AI client
ai_client = ChatCompletionsClient(
    endpoint="https://models.github.ai/inference",
    credential=AzureKeyCredential(AI_TOKEN),
)

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use environment variables in production

# Telegram bot app
bot_app = Application.builder().token(TOKEN).build()



async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'option_1':
        await query.edit_message_text("You selected Option 1. Number: 10")
    elif query.data == 'option_2':
        await query.edit_message_text("You selected Option 2. Number: 11")

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


def build_category_response(rows):
    if not rows:
        return "ℹ️ No categories found for this Sazman ID.", None

    # Each category becomes a button
    keyboard = [
        [InlineKeyboardButton(text=row.Name, callback_data=f"category_{row.Id}")]
        for row in rows
    ]

    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return "📂 لطفا یک دسته بندی را انتخاب کنید:", reply_markup

def build_query_response(result_text: str):
    if not result_text:
        result_text = "❌ No results available for this page."
    keyboard = [[InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_pages")]]
    return result_text, InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    sazman_id = is_user_authorized(telegram_id)

    # Detect source of the update: message or callback
    if update.message:
        send_func = update.message.reply_text
    elif update.callback_query:
        send_func = update.callback_query.message.reply_text
    else:
        return
    
    if sazman_id:
        sazman_title = get_sazman_title_from_sazman_id(sazman_id)
        await send_func(f"✅ دسترسی شما تایید شد. سازمان شما: {sazman_title}")

        rows = get_categories_by_sazman_id(sazman_id)
        if rows is not None:
            text, reply_markup = build_category_response(rows)
            await send_func(text, reply_markup=reply_markup)
        else:
            await send_func("❌ خطا در گرفتن دسته بندی ها از دیتابیس.")
    else:
        await send_func(
            f"❌ شما اجازه دسترسی به این ربات را ندارید. لطفاً با مدیر تماس بگیرید.\n\n"
            f"آیدی تلگرام جهت تعریف: <code>{telegram_id}</code>",
            parse_mode='HTML'
        )


def get_pages_by_category_id(category_id: int):
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
  
def get_query_results_by_page_id(page_id: int):
    db: Session = SessionLocal()
    try:
        records = db.query(DashboardPageConnection).filter_by(page_id=page_id)
        # return user.sazman_id if user else None
        temps = []
        for record in records:
            if record:
                connection_string = record.connection_string
                query_text = record.query
                query_title = record.query_title
                print("Connection String:", connection_string)
                print("Query:", query_text)
            else:
                print("No record found with that page_id.")
            
            try:
                conn = get_sqlserver_connection(conn_str=connection_string)
                cursor = conn.cursor()
                cursor.execute(query_text)
                temp = cursor.fetchall()
                temps.append((query_title, temp))
                
            except Exception as e:
                logger.error(f"SQL Server error while fetching queries: {e}")
                return None
            finally:
                if 'conn' in locals():
                    conn.close()
        return temps
    finally:
        db.close()
        

def build_page_response(rows):
    if not rows:
        return "ℹ️ No pages found for this category.", None

    keyboard = [
        [InlineKeyboardButton(text=row.Title, callback_data=f"page_{row.Id}")]
        for row in rows
    ]
    # Add back button to go to categories
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_categories")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return "📄 لطفا یک صفحه را انتخاب کنید:", reply_markup

async def handle_category_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ handle_category_click triggered!")  # Debug print
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="⏳ لطفا صبر کنید...")

    category_id = int(query.data.split("_")[1])
    print(f"➡️ Category ID: {category_id}")
    
    context.user_data["last_category_id"] = category_id
    
    pages = get_pages_by_category_id(category_id)
    print(f"Fetched {len(pages)} pages") if pages else print("No pages found")

    text, reply_markup = build_page_response(pages)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_page_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ handle_page_click triggered!")  # Debug print
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="⏳ لطفا صبر کنید...")
    
    page_id = int(query.data.split("_")[1])
    print(f"➡️ Page ID: {page_id}")

    context.user_data["last_page_id"] = page_id
    
    temps = get_query_results_by_page_id(page_id)
    
    # print(f"Fetched {len(queries)} queris") if queries else print("No queries found")
    resutlt_text = ""
    for temp in temps:
        result_text = f"{temp[0]}: {temp[1][0][0]}" if temp[1] else f"{temp[0]}: بدون نتیجه"
        resutlt_text += result_text + "\n\n"
    
    # if temps:
    #     resutlt_text = f" {str(queries[0][0])}"
    # else:
    #     resutlt_text = None
        
    # resutlt_text = 'جمع کل مانده: 54100000 \nجمع کل مانده2: 584600000'
    text, reply_markup = build_query_response(result_text=resutlt_text)
    await query.edit_message_text(text=text, reply_markup=reply_markup)



async def handle_back_to_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = str(query.from_user.id)
    sazman_id = is_user_authorized(telegram_id)
    rows = get_categories_by_sazman_id(sazman_id)

    text, reply_markup = build_category_response(rows)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_back_to_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Store category ID in context for reuse
    category_id = context.user_data.get("last_category_id")
    if category_id is None:
        await query.edit_message_text("❌ اطلاعات دسته‌بندی در دسترس نیست.")
        return

    pages = get_pages_by_category_id(category_id)
    text, reply_markup = build_page_response(pages)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def handle_back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)  # Reuse start logic





bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_category_click, pattern=r'^category_\d+$'))
bot_app.add_handler(CallbackQueryHandler(handle_page_click, pattern=r'^page_\d+$'))
bot_app.add_handler(CallbackQueryHandler(handle_back_to_categories, pattern='^back_to_categories$'))
bot_app.add_handler(CallbackQueryHandler(handle_back_to_pages, pattern='^back_to_pages$'))
bot_app.add_handler(CallbackQueryHandler(handle_back_to_start, pattern='^back_to_start$'))



async def debug_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print("Callback data received:", query.data)
    await query.answer("debug")

bot_app.add_handler(CallbackQueryHandler(debug_all_callbacks))  # Add this temporarily to catch all callback data


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


####################################### Logging setup #######################################
from flask import Flask, render_template, request, redirect, session, url_for
from db import SessionLocal, TelegramUser, DashboardPageConnection, AdminUser
from sqlalchemy.orm.exc import NoResultFound

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        db = SessionLocal()
        try:
            user = db.query(AdminUser).filter_by(phone=phone, password=password).one()
            session['admin'] = user.phone
            return redirect('/dashboard')
        except NoResultFound:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/add-telegram-user', methods=['GET', 'POST'])
def add_telegram_user():
    if 'admin' not in session:
        return redirect('/')
    if request.method == 'POST':
        telegram_user_id = request.form['telegram_user_id']
        sazman_id = request.form['sazman_id']
        db = SessionLocal()
        db.add(TelegramUser(telegram_user_id=telegram_user_id, sazman_id=sazman_id))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_telegram_user.html')

@app.route('/add-page-connection', methods=['GET', 'POST'])
def add_page_connection():
    if 'admin' not in session:
        return redirect('/')
    if request.method == 'POST':
        db = SessionLocal()
        db.add(DashboardPageConnection(
            query_title=request.form['query_title'],
            page_id=request.form['page_id'],
            connection_string=request.form['connection_string'],
            query=request.form['query']
        ))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_page_connection.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == "__main__":
    
    # Initialize bot before starting the server
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.start())

    print("Starting server with Waitress...")
    serve(app, host="0.0.0.0", port=9090)

