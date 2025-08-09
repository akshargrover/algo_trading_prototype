import gspread
import os
import json
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load env variables
load_dotenv()
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

if not GOOGLE_CREDS_JSON:
    raise ValueError("Google credentials JSON not found in environment variables.")

# Convert JSON string from .env to dict
creds_dict = json.loads(GOOGLE_CREDS_JSON)

# Authorize Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME)

def log_trades_to_sheet(trades, sheet_name):
    try:
        worksheet = sheet.worksheet(sheet_name)
    except:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
    worksheet.clear()
    worksheet.update([trades.columns.values.tolist()] + trades.values.tolist())
