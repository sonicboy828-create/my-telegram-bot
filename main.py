import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# 1. Google Sheets API ချိတ်ဆက်ခြင်း
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
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
            # Sheet ထဲရှိ ပစ္စည်းနာမည် (column နာမည်ကို လိုအပ်သလို ပြင်နိုင်ပါသည်)
            item_name = str(row.get("Item", "")) # Sheet ထဲက col နာမည် 'Item' ဟု ယူဆပါသည်
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
        await update.message.reply_text(f"❌ Google Sheet ကို ချိတ်ဆက်၍ မရပါ။ credentials.json နှင့် Sheet နာမည်ကို စစ်ဆေးပါ။[span_0](start_span)[span_0](end_span)")

# 4. Bot ကို စတင်လည်ပတ်စေရန် (Main Function)
def main():
    # Telegram Bot Token ကို Render Environment Variable မှ ယူမည် (သို့မဟုတ် တိုက်ရိုက်ထည့်နိုင်သည်)
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_item))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
