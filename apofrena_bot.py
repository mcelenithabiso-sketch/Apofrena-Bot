import os, logging, threading, requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
@app.route('/')
def home(): return "Apofrena Bot is LIVE!"
def run_flask(): app.run(host="0.0.0.0", port=PORT)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Crypto Signal", callback_data="sig_crypto"),
         InlineKeyboardButton("💱 Forex Signal", callback_data="sig_forex")],
        [InlineKeyboardButton("💰 Crypto Price", callback_data="price_crypto"),
         InlineKeyboardButton("💵 Forex Price", callback_data="price_forex")],
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

# --- PRICE HELPERS ---
def crypto_price(sym):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}USDT", timeout=10)
        return float(r.json()['price'])
    except: return None

def forex_price(pair):
    # pair like EURUSD, GBPUSD, USDJPY, XAUUSD
    try:
        if pair == "XAUUSD":
            r = requests.get("https://data-asg.goldprice.org/db_XAUUSD.json", timeout=10).json()
            return float(r['items'][0]['curr'])
        base, quote = pair[:3], pair[3:]
        r = requests.get(f"https://api.exchangerate.host/convert?from={base}&to={quote}", timeout=10).json()
        return float(r['result'])
    except: return None

def crypto_signal(sym="BTC"):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}USDT", timeout=10).json()
        ch = float(r['priceChangePercent']); price = float(r['lastPrice'])
        sig = "🟢 BUY - Momentum Up" if ch > 1 else "🔴 SELL - Momentum Down" if ch < -1 else "🟡 WAIT - Sideways"
        return f"🪙 *{sym} Signal:*\n{sig}\nPrice: ${price:,.2f}\n24h Change: {ch:.2f}%"
    except: return "⚠️ Crypto signal unavailable, try again."

def forex_signal(pair="EURUSD"):
    try:
        # Use 24h logic via simple trend: compare today vs yesterday using exchangerate history is complex,
        # so we use volatility + current rate as signal placeholder with live price
        price = forex_price(pair)
        if not price: return "⚠️ Forex signal unavailable."
        # Simple rule: Gold > 2000 = Bullish, EURUSD > 1.08 = Bullish etc - for demo, use price levels
        if pair == "XAUUSD":
            sig = "🟢 BUY - Gold Bullish" if price > 2000 else "🟡 WAIT - Gold Consolidating"
        elif pair == "EURUSD":
            sig = "🟢 BUY EUR" if price > 1.08 else "🔴 SELL EUR" if price < 1.05 else "🟡 WAIT"
        elif pair == "GBPUSD":
            sig = "🟢 BUY GBP" if price > 1.27 else "🔴 SELL GBP" if price < 1.24 else "🟡 WAIT"
        else:
            sig = "🟡 WAIT - Check Chart"
        return f"💱 *{pair} Signal:*\n{sig}\nLive Price: {price:,.4f}"
    except: return "⚠️ Forex signal unavailable."

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 *Welcome to Apofrena Bot!*\n\n🪙 Crypto + 💱 Forex Signals LIVE.\nTap a button:", parse_mode="Markdown", reply_markup=main_menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Commands:*\n/start - Menu\n/signal_crypto BTC - Crypto signal\n/signal_forex EURUSD - Forex signal\n/price BTC - Crypto price\n/price_forex EURUSD - Forex price\n/status - Status",
        parse_mode="Markdown", reply_markup=main_menu())

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Apofrena LIVE\n🪙 Crypto: ON\n💱 Forex: ON\n🟢 Running on Render", reply_markup=main_menu())

async def price_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sym = context.args[0].upper() if context.args else "BTC"
    p = crypto_price(sym)
    await update.message.reply_text(f"💰 *{sym}/USDT:* `${p:,.2f}`" if p else "❌ Try /price BTC, ETH, SOL", parse_mode="Markdown", reply_markup=main_menu())

async def price_forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else "EURUSD"
    p = forex_price(pair)
    await update.message.reply_text(f"💵 *{pair}:* `{p:,.4f}`" if p else "❌ Try /price_forex EURUSD, GBPUSD, XAUUSD", parse_mode="Markdown", reply_markup=main_menu())

async def sig_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sym = context.args[0].upper() if context.args else "BTC"
    await update.message.reply_text(crypto_signal(sym), parse_mode="Markdown", reply_markup=main_menu())

async def sig_forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else "EURUSD"
    await update.message.reply_text(forex_signal(pair), parse_mode="Markdown", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback
