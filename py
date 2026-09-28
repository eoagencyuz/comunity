import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Maxfiy kalitlar (Render sozlamalaridan olinadi)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI sozlamasi
genai.configure(api_key=GEMINI_KEY)

# Bilimlar bazasini o'qish
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
except Exception:
    knowledge_base = "Kompaniya haqida ma'lumot."

system_instruction = f"""
Sen aqlli, xushmuomala yordamchi AI agentsan.
Mijozlarga quyidagi ma'lumotlar bazasi asosida aniq va lo'nda javob ber:
{knowledge_base}

QAT'IY QOIDA: Agar berilgan savolga ushbu bazada javob bo'lmasa, to'qima ma'lumot aytma.
"Ushbu masala bo'yicha mutaxassisimiz siz bilan bog'lanadi" deb javob ber.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# FastAPI va Telegram ilovasi
app = FastAPI()
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start_command(update: Update, context):
    await update.message.reply_text("Assalomu alaykum! Savolingizni bering, sizga yordam berishdan mamnunman.")

async def handle_message(update: Update, context):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        reply = response.text
    except Exception:
        reply = "Kechirasiz, tizimda qisqa uzilish bo'ldi. Birozdan so'ng qayta urinib ko'ring."
    
    await update.message.reply_text(reply)

# Buyruqlarni ro'yxatga olish
tg_app.add_handler(CommandHandler("start", start_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# UptimeRobot va tekshiruv uchun eshik (server uxlamasligi uchun)
@app.get("/")
def home():
    return {"status": "Tizim 24/7 faol ishlamoqda!"}

# Telegram Webhook qabul qiluvchi manzil
@app.post("/webhook")
async def telegram_webhook(request: Request):
    req_data = await request.json()
    update = Update.de_json(req_data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await tg_app.initialize()
    await tg_app.start()
