import pandas as pd
import ta
import numpy as np
import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from indicators import Indicators

@dataclass
class Trade:
    ticker: str
    entry_date: datetime.date
    entry_price: float
    exit_date: Optional[datetime.date] = None
    exit_price: Optional[float] = None
    size: float = 1.0

    def pnl(self) -> Optional[float]:
        if self.exit_price is None:
            return None
        return (self.exit_price - self.entry_price) * self.size


class Strategy:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare()

    def _prepare(self):
        self.df["close"] = self.df["Close"]
        self.df["rsi"] = Indicators.rsi(self.df["close"]) 
        self.df["sma20"] = Indicators.sma(self.df["close"], 20)
        self.df["sma50"] = Indicators.sma(self.df["close"], 50)
        macd_df = Indicators.macd(self.df["close"]) 
        self.df = pd.concat([self.df, macd_df], axis=1)

    def generate_signals(self) -> pd.DataFrame:
        df = self.df.copy()
        df["rsi_buy"] = df["rsi"] < 30
        # sma cross: today sma20 > sma50 and yesterday sma20 <= sma50
        df["sma_cross"] = (df["sma20"] > df["sma50"]) & (df["sma20"].shift(1) <= df["sma50"].shift(1))
        df["buy_signal"] = df["rsi_buy"] & df["sma_cross"]
        # Sell rule (example): RSI > 70 or sma20 crosses below sma50
        df["rsi_sell"] = df["rsi"] > 70
        df["sma_cross_down"] = (df["sma20"] < df["sma50"]) & (df["sma20"].shift(1) >= df["sma50"].shift(1))
        df["sell_signal"] = df["rsi_sell"] | df["sma_cross_down"]
        return df
