import os
import asyncio
import schedule
import time
import threading
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Apofrena Bot is LIVE! Send /report for daily report.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 APOFRENA DAILY REPORT - 18:00\n\nBot is running ✅\nGold + Forex signals coming soon.\nNext report: Tomorrow 18:00")

async def send_daily_report(app):
    try:
        await app.bot.send_message(chat_id=CHAT_ID, text="📊 APOFRENA DAILY REPORT - 18:00\n\nBot is running ✅\nYour 18:00 report is working!\nTomorrow same time.")
        print("Report sent")
    except Exception as e:
        print(f"Error: {e}")

def run_schedule(app):
    schedule.every().day.at("18:00").do(lambda: asyncio.run_coroutine_threadsafe(send_daily_report(app), app.loop))
    while True:
        schedule.run_pending()
        time.sleep(60)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    
    # Start scheduler in background
    threading.Thread(target=run_schedule, args=(app,), daemon=True).start()
    
    print("Bot Started")
    # Send started message
    try:
        await app.bot.send_message(chat_id=CHAT_ID, text="🤖 Apofrena Bot Started - Running on Render")
    except Exception as e:
        print(e)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
