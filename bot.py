import os
import anthropic
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# === Config ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
SHEET_ID = os.environ.get("SHEET_ID")

# === เชื่อม Google Sheet ===
import json
credentials_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
gc = gspread.service_account_from_dict(credentials_json)
sheet = gc.open_by_key(SHEET_ID).sheet1

# === เชื่อม Claude ===
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# === ฟังก์ชันตอบคำถาม ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    
    # ดึงข้อมูลจาก Google Sheet
    data = sheet.get_all_records()
    
    # ส่งให้ Claude ตอบ
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=f"คุณคือ AI Assistant ที่ตอบคำถามโดยอ้างอิงข้อมูลจาก Google Sheet นี้เท่านั้น:\n{data}",
        messages=[{"role": "user", "content": question}]
    )
    
    await update.message.reply_text(response.content[0].text)

# === รัน Bot ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()