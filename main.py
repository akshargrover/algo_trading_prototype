import logging
import os
from dotenv import load_dotenv
from data_fetcher import fetch_stock_data
from strategy import apply_indicators
from backtester import backtest
from sheets_logger import log_trades_to_sheet
from ml_model import train_predictor
from utils import setup_logger

load_dotenv()
TICKERS = os.getenv("TICKERS").split(",")

def run_algo():
    setup_logger()
    for ticker in TICKERS:
        logging.info(f"Processing {ticker}...")

        df = fetch_stock_data(ticker)
        df = apply_indicators(df)

        trades = backtest(df, ticker)
        if not trades.empty:
            log_trades_to_sheet(trades, ticker.replace(".NS", ""))

        accuracy = train_predictor(df)
        logging.info(f"Prediction accuracy for {ticker}: {accuracy:.2f}")

if __name__ == "__main__":
    run_algo()
