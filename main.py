import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Credentials ကို ချိတ်ဆက်ရန် (Render မှာ Secret File သုံးထားရင် ဖိုင်နာမည် 'credentials.json' လို့ ပေးရပါမယ်)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 2. Google Sheet နာမည်ကို အတိအကျ ခေါ်ရန်
# Sheet နာမည်က 'MT worksheet' ဖြစ်တဲ့အတွက် အောက်ပါအတိုင်း ဖြစ်ရပါမယ်
sheet = client.open("MT worksheet").sheet1  # ပထမဆုံး Sheet (Tab) ကို ယူသုံးရန်
