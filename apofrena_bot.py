import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Apofrena Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_price(symbol="BTC"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        r = requests.get(url, timeout=5)
        return float(r.json()["price"])
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Get Signal", callback_data="signal")],
        [InlineKeyboardButton("💰 BTC Price", callback_data="price_BTC"),
         InlineKeyboardButton("💰 ETH Price", callback_data="price_ETH")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 *Welcome to Apofrena Bot!*\n\nChoose an option below:", reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "signal":
        btc = get_price("BTC")
        eth = get_price("ETH")
        msg = f"📊 *LIVE SIGNAL*\n\nBTC: ${btc:,.2f}\nETH: ${eth:,.2f}\n\nTrend: Watch BTC breakout above resistance." if btc else "Signal unavailable, try again."
        await query.message.reply_text(msg, parse_mode="Markdown")
    elif data.startswith("price_"):
        sym = data.split("_")[1]
        price = get_price(sym)
        await query.message.reply_text(f"💰 {sym}: ${price:,.2f}" if price else "Price unavailable")
    elif data == "help":
        await query.message.reply_text("/start - Menu\nSend /start anytime to get buttons.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

print("Apofrena Bot starting...")
app_bot = ApplicationBuilder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("help", help_command))
app_bot.add_handler(CallbackQueryHandler(button_handler))

bot_thread = threading.Thread(target=run_bot, args=(app_bot,), daemon=True)
bot_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
