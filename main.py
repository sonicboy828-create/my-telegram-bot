import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# 1. Google Sheets API နှင့် Credentials ချိတ်ဆက်ခြင်း
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Render တွင် Secret File သိမ်းဆည်းသည့် လမ်းကြောင်းအတိုင်း ချိတ်ဆက်ရန်
cred_path = "/etc/secrets/credentials.json"
if not os.path.exists(cred_path):
    cred_path = "credentials.json"  # Local (Computer) တွင် စမ်းသပ်ရန်

creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

# Google Sheet နာမည် 'MT worksheet' ကို ချိတ်ဆက်ခြင်း
sheet = client.open("MT worksheet").sheet1

# 2. /start အမိန့်ပေးသည့်အခါ တုံ့ပြန်ရန်
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 မင်္ဂလာပါ အကို။ 31's Items ဈေးနှုန်းနှင့် ရှာဖွေရေး Bot (Google Sheet Version) ဖြစ်ပါတယ်။\n\n"
        "🔍 ပစ္စည်းနာမည်ရဲ့ စာလုံးအစကို ရိုက်ထည့်ပြီး ရှာဖွေနိုင်ပါတယ်ဗျာ။"
    )
    await update.message.reply_text(welcome_message)

# 3. Telegram မှ စာပို့လာပါက Google Sheet ထဲတွင် ရှာဖွေရန်
async def search_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    try:
        # Sheet ထဲက ဒေတာအားလုံးကို ဆွဲထုတ်ခြင်း
        data = sheet.get_all_records()
        
        found_results = []
        for row in data:
            # Sheet ထဲရှိ ပစ္စည်းနာမည် (Column နာမည် 'Item' ဟု ယူဆပါသည်)
            item_name = str(row.get("Item", "")) 
            if query.lower() in item_name.lower():
                found_results.append(row)
                
        if found_results:
            response_text = ""
            for item in found_results:
                # ပြန်ပြမည့် ပုံစံ (Sheet ထဲက Column ခေါင်းစဉ်များအတိုင်း ထည့်ပါ)
                response_text += f"📦 ပစ္စည်း: {item.get('Item')}\n💰 ဈေးနှုန်း: {item.get('Price')}\n-------------------\n"
            await update.message.reply_text(response_text)
        else:
            await update.message.reply_text(f"❌ '{query}' ဆိုသော ပစ္စည်းကို ရှမတွေ့ပါ စာလုံးပေါင်း သေချာစစ်ဆေးပါ။")
            
    except Exception as e:
        await update.message.reply_text("❌ Google Sheet ကို ချိတ်ဆက်၍ မရပါ။ credentials.json နှင့် Sheet နာမည်ကို စစ်ဆေးပါ။")

# 4. Bot ကို စတင်လည်ပတ်စေရန် (Main Function)
def main():
    # Telegram Bot Token ကို Render Environment Variable (BOT_TOKEN) မှ ယူမည်
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: BOT_TOKEN is not set in environment variables.")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_item))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
