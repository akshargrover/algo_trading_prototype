import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import dotenv

dotenv.load_dotenv()

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
client = gspread.authorize(creds)

sheet = client.open("AlgoTrade Log")


def log_trades_to_sheet(trades: pd.DataFrame, sheet_name: str):
    try:
        worksheet = sheet.worksheet(sheet_name)
    except:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
    worksheet.clear()
    worksheet.update([trades.columns.values.tolist()] + trades.values.tolist())
