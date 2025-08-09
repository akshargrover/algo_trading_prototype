from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
TICKERS = os.getenv("TICKERS").split(",")
