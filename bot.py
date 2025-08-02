import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from openai import OpenAI

# 🔐 Получаем ключи из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔧 Настройка клиентов
app = FastAPI()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
application: Application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 📌 Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я GPT-бот, работаю 24/7!")

# 📌 Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        chat_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        reply_text = chat_response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"⚠️ Ошибка GPT: {e}"

    await update.message.reply_text(reply_text)

# 📌 Подключение обработчиков Telegram
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 📌 Запуск Telegram-приложения при старте FastAPI
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()

@app.on_event("shutdown")
async def shutdown():
    await application.stop()

# 📌 Webhook от Telegram
@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}
