import argparse
from config import DEFAULT_TICKERS, LOG
from data_fetcher import DataFetcher
from logging import GSheetsLogger, GSHEETS_AVAILABLE
from ml_model import run_ml_for_ticker
from orchestration import run_backtest_for_tickers, scan_and_log
import os 
def cli():
    parser = argparse.ArgumentParser(description="Mini algo-trading prototype CLI")
    parser.add_argument("--tickers", nargs="*", default=DEFAULT_TICKERS, help="Tickers list")
    parser.add_argument("--run-backtest", action="store_true")
    parser.add_argument("--scan", action="store_true", help="Run a fresh scan and optionally log to Google Sheets")
    parser.add_argument("--ml", action="store_true", help="Run ML model for each ticker")
    parser.add_argument("--use-gsheets", action="store_true", help="Push logs to Google Sheets (requires creds)")
    args = parser.parse_args()

    if args.run_backtest:
        LOG.info("Running backtest...")
        results = run_backtest_for_tickers(args.tickers)
        for t, res in results.items():
            LOG.info(f"{t} => summary: {res['summary']}")

    if args.ml:
        LOG.info("Running ML models... (this may take a little while)")
        fetcher = DataFetcher(tickers=args.tickers, period="6mo")
        all_data = fetcher.fetch()
        for t, df in all_data.items():
            ml_res = run_ml_for_ticker(df, model_type="tree")
            LOG.info(f"{t} => ML: {ml_res}")

    if args.scan:
        LOG.info("Running scan...")
        gsheet = None
        if args.use_gsheets:
            if not GSHEETS_AVAILABLE:
                LOG.error("gspread not installed or not configured. Install gspread and google-auth.")
            else:
                gsheet = GSheetsLogger(cred_json=os.environ.get("GSHEET_CRED_JSON"), spreadsheet_name=os.environ.get("GSHEET_SPREADSHEET_NAME"))
        trades, summary = scan_and_log(args.tickers, gsheet=gsheet)
        LOG.info(f"Scan results: {summary}")


if __name__ == "__main__":
    cli()
