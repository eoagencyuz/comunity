import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from groq import Groq

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
except Exception:
    knowledge_base = "Kompaniya haqida ma'lumot."

system_instruction = f"""
Sen aqlli va xushmuomala yordamchi AI agentsan.
Mijozlarga faqat quyidagi ma'lumotlar bazasi asosida aniq va lo'nda javob ber:
{knowledge_base}

QAT'IY QOIDA: Agar berilgan savolga ushbu bazada javob bo'lmasa, to'qima ma'lumot aytma.
"Ushbu masala bo'yicha mutaxassisimiz siz bilan bog'lanadi" deb javob ber.
"""

app = FastAPI()
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start_command(update: Update, context):
    await update.message.reply_text("Assalomu alaykum! Savolingizni bering, yordam berishdan mamnunman.")

async def handle_message(update: Update, context):
    user_text = update.message.text
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0.3
        )
        reply = completion.choices[0].message.content
    except Exception:
        reply = "Kechirasiz, tizimda qisqa uzilish bo'ldi. Birozdan so'ng qayta urinib ko'ring."
    
    await update.message.reply_text(reply)

tg_app.add_handler(CommandHandler("start", start_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.get("/")
def home():
    return {"status": "Tizim 24/7 faol ishlamoqda!"}

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
