import os
import threading
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# 1. Render Port Error မတက်စေရန် Flask Web Server ကို ချက်ချင်းစတင်ခြင်း
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

# Global variables
sheet = None

def init_google_sheet():
    global sheet
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        cred_path = "/etc/secrets/credentials.json"
        if not os.path.exists(cred_path):
            cred_path = "credentials.json"

        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open("MT worksheet").sheet1
        print("Google Sheet connected successfully!")
    except Exception as e:
        print(f"Google Sheet Connection Error: {e}")

# Telegram Bot Commands & Message Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 မင်္ဂလာပါ အကို။ 31's Items ဈေးနှုန်းနှင့် ရှာဖွေရေး Bot ဖြစ်ပါတယ်။\n\n"
        "🔍 ပစ္စည်းနာမည်ရဲ့ စာလုံးအစကို ရိုက်ထည့်ပြီး ရှာဖွေနိုင်ပါတယ်ဗျာ။"
    )
    await update.message.reply_text(welcome_message)

async def search_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sheet
    if not sheet:
        await update.message.reply_text("❌ Google Sheet ချိတ်ဆက်နေဆဲ ဖြစ်ပါသည် ခဏစောင့်ပါ။")
        return

    query = update.message.text.strip()
    
    try:
        data = sheet.get_all_records()
        
        found_results = []
        for row in data:
            item_name = str(row.get("Item", "")) 
            if query.lower() in item_name.lower():
                found_results.append(row)
                
        if found_results:
            response_text = ""
            for item in found_results:
                response_text += f"📦 ပစ္စည်း: {item.get('Item')}\n💰 ဈေးနှုန်း: {item.get('Price')}\n-------------------\n"
            await update.message.reply_text(response_text)
        else:
            await update.message.reply_text(f"❌ '{query}' ဆိုသော ပစ္စည်းကို ရှမတွေ့ပါ စာလုံးပေါင်း သေချာစစ်ဆေးပါ။")
            
    except Exception as e:
        await update.message.reply_text("❌ ဒေတာဖတ်ရှုရာတွင် အမှားအယွင်းရှိပါသည်ဆစစ်ဆေးပါ။")

def run_telegram_bot():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set in environment variables.")
        return

    # Google Sheet ကို Background Thread ဖြင့် ချိတ်ဆက်ခြင်း
    init_google_sheet()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_item))
    
    print("Telegram Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Telegram Bot ကို Background Thread ဖြင့် ဖွင့်ခြင်း
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.start()
    
    # Render မှပေးမည့် Port ဖြင့် Flask Server ကို ချက်ချင်းစတင်ခြင်း (Port Timeout ကာကွယ်ရန်)
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
