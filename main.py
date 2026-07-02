import os
import logging
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8673757379:AAGOKLwkHxDZaIOD09MDqzYByACKVJW5JpE"
EXCEL_FILE = "31_items_clean_list.xlsx"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "👋 မင်္ဂလာပါ အကို။ 31's Items စျေးနှုန်းရှာဖွေရေး Bot ဖြစ်ပါတယ်။\n\n"
        "🔍 ပစ္စည်းအမည်ရဲ့ စာလုံးအစကို ရိုက်ထည့်ပြီး ရှာဖွေနိုင်ပါတယ်ဗျာ။"
    )
    await update.message.reply_text(welcome_text)

def search_items(query):
    query = str(query).strip().lower()
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        return "❌ Excel ဖိုင်ကို ဖတ်လို့မရပါ။"
    
    results = df[df['Items & Types'].str.lower().str.contains(query, na=False)]
    if results.empty:
        return f"❌ '{query}' နှင့် ပတ်သက်သည့် ပစ္စည်းစာရင်း မရှိပါဗျာ။"
    
    output = f"🔍 **'{query}' အတွက် ရှာဖွေမှုရလဒ် ({len(results)} ခု တွေ့ရှိ):**\n\n"
    for idx, row in results.head(10).iterrows():
        item_name = row['Items & Types']
        case_p = f"{row['P-Prices (Case)']:,.0f}" if row['P-Prices (Case)'] > 0 else "မရှိပါ"
        pack = row['Pack Size']
        unit_p = f"{row['Unit-P-Prices']:,.0f}" if row['Unit-P-Prices'] > 0 else "0"
        sales_p = f"{row['Unit Sales Prices']:,.0f}" if row['Unit Sales Prices'] > 0 else "0"
        profit_u = f"{row['Profit Per Unit']:,.0f}" if row['Profit Per Unit'] > 0 else "0"
        
        output += f"🍺 **{item_name}**\n"
        output += f"   • ဝယ်စျေး (ဖာ): {case_p} MMK ({pack} ဗူးဝင်)\n"
        output += f"   • ဝယ်စျေး (ဗူး): {unit_p} MMK\n"
        output += f"   • ရောင်းစျေး (ဗူး): {sales_p} MMK\n"
        output += f"   • အမြတ် (ဗူး): {profit_u} MMK\n"
        output += f"----------------------------------------\n"
    return output

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    reply_text = search_items(user_text)
    await update.message.reply_text(reply_text, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Render cloud server ပေါ်မှာ run ဖို့ web port ဖွင့်ပေးခြင်း
    from flask import Flask
    import threading
    flask_app = Flask('')
    @flask_app.route('/')
    def home(): return "Bot is Alive"
    def run(): flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    threading.Thread(target=run).start()
    
    app.run_polling()

if __name__ == '__main__':
    main()
