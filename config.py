import logging
import os 


LOG = logging.getLogger("algo_proto")
LOG.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
LOG.addHandler(ch)

DEFAULT_TICKERS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]  # examples from NIFTY 50
DATA_DIR = "./data"
GSHEET_CRED_JSON = os.environ.get("GSHEET_CRED_JSON", "gcp_service_account.json")
GSHEET_SPREADSHEET_NAME = os.environ.get("GSHEET_SPREADSHEET_NAME", "algo_trading_log")