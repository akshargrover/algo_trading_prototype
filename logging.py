from typing import List
from strategy import Trade
from config import GSHEET_CRED_JSON, GSHEET_SPREADSHEET_NAME

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except Exception:
    GSHEETS_AVAILABLE = False

class GSheetsLogger:
    def __init__(self, cred_json: str = GSHEET_CRED_JSON, spreadsheet_name: str = GSHEET_SPREADSHEET_NAME):
        if not GSHEETS_AVAILABLE:
            raise ImportError("gspread/google oauth not installed or available")
        self.cred_json = cred_json
        self.spreadsheet_name = spreadsheet_name
        self.client = self._auth()
        self.sheet = self._open()

    def _auth(self):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(self.cred_json, scopes=scopes)
        client = gspread.authorize(creds)
        return client

    def _open(self):
        try:
            sh = self.client.open(self.spreadsheet_name)
        except Exception:
            sh = self.client.create(self.spreadsheet_name)
        return sh

    def write_trade_log(self, trades: List[Trade], tab_name: str = "trade_log"):
        ws = None
        try:
            ws = self.sheet.worksheet(tab_name)
        except Exception:
            ws = self.sheet.add_worksheet(title=tab_name, rows="1000", cols="20")
        header = ["ticker", "entry_date", "entry_price", "exit_date", "exit_price", "size", "pnl"]
        rows = [header]
        for t in trades:
            rows.append([t.ticker, str(t.entry_date), t.entry_price, str(t.exit_date), t.exit_price, t.size, t.pnl()])
        ws.update(rows)

    def write_summary(self, summary: dict, tab_name: str = "summary"):
        try:
            ws = self.sheet.worksheet(tab_name)
        except Exception:
            ws = self.sheet.add_worksheet(title=tab_name, rows="100", cols="10")
        rows = [[k, v] for k, v in summary.items()]
        ws.update(rows)