import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from utils import ensure_data_dir
from config import DATA_DIR
from config import LOG
import os 

# Configure logging
class DataFetcher:
    """Fetches daily data for tickers using yfinance. Saves to CSV cache.
    """

    def __init__(self, tickers: List[str], period: str = "6mo", interval: str = "1d"):
        self.tickers = tickers
        self.period = period
        self.interval = interval
        ensure_data_dir()

    def fetch(self, force_refresh: bool = False) -> dict:
        result = {}
        for t in self.tickers:
            path = os.path.join(DATA_DIR, f"{t.replace('.', '_')}.csv")
            if (not force_refresh) and os.path.exists(path):
                try:
                    df = pd.read_csv(path, index_col=0, parse_dates=True)
                    # if last date is recent enough, keep cached
                    if (datetime.datetime.now() - df.index[-1].to_pydatetime()).days < 2:
                        LOG.info(f"Loaded cached data for {t} from {path}")
                        result[t] = df
                        continue
                except Exception:
                    LOG.exception("Failed to load cache, refetching")

            LOG.info(f"Fetching {t} from yfinance")
            yf_ticker = yf.Ticker(t)
            df = yf_ticker.history(period=self.period, interval=self.interval, auto_adjust=False)
            if df.empty:
                LOG.warning(f"No data for {t}")
                continue
            df.to_csv(path)
            result[t] = df
        return result
