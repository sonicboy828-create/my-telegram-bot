import os
import threading
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# 1. Flask Web Server (Render Port အတွက်)
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

# Google Sheet ချိတ်ဆက်ခြင်း
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_path = "/etc/secrets/credentials.json"
if not os.path.exists(cred_path):
    cred_path = "credentials.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)
sheet = client.open("MT worksheet").sheet1

# Telegram Bot Commands & Message Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 မင်္ဂလာပါ အကို။ 31's Items ဈေးနှုန်းနှင့် ရှာဖွေရေး Bot ဖြစ်ပါတယ်။\n\n"
        "🔍 ပစ္စည်းနာမည်ရဲ့ စာလုံးအစကို ရိုက်ထည့်ပြီး ရှာဖွေနိုင်ပါတယ်ဗျာ။"
    )
    await update.message.reply_text(welcome_message)

async def search_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("❌ ဒေတာဖတ်ရှုရာတွင် အမှားအယွင်းရှိပါသည် စစ်ဆေးပါ။")

if __name__ == "__main__":
    # Flask ဆာဗာကို Background Thread ဖြင့် စတင်ခြင်း (Render Port ဖြေရှင်းရန်)
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        app_flask.run(host="0.0.0.0", port=port)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Telegram Bot ကို Main Thread တွင် တိုက်ရိုက် run ခြင်း (Error လုံးဝမတက်စေရန်)
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set in environment variables.")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_item))
        
        print("Telegram Bot is running successfully...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
