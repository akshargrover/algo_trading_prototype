import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from strategy import Trade
from config import LOG



class Backtester:
    def __init__(self, signals_df: pd.DataFrame, ticker: str, starting_cash: float = 100000.0):
        self.signals = signals_df
        self.ticker = ticker
        self.starting_cash = starting_cash
        self.trades: List[Trade] = []

    def run(self):
        cash = self.starting_cash
        position = None  # Trade object
        for idx, row in self.signals.iterrows():
            date = idx.date()
            close = row["Close"]
            if position is None and row.get("buy_signal", False):
                size = cash // close  # integer shares
                if size <= 0:
                    continue
                position = Trade(ticker=self.ticker, entry_date=date, entry_price=close, size=size)
                cash -= size * close
                LOG.info(f"{self.ticker} BUY on {date} @ {close} size={size}")
            elif position is not None and row.get("sell_signal", False):
                position.exit_date = date
                position.exit_price = close
                cash += position.size * close
                LOG.info(f"{self.ticker} SELL on {date} @ {close} size={position.size}")
                self.trades.append(position)
                position = None
        # close any open position at last price
        if position is not None:
            last_price = self.signals.iloc[-1]["Close"]
            position.exit_date = self.signals.index[-1].date()
            position.exit_price = last_price
            cash += position.size * last_price
            self.trades.append(position)
            position = None
        final_value = cash
        return self.trades, final_value

    def summary(self):
        wins = 0
        losses = 0
        total_pnl = 0.0
        for t in self.trades:
            pnl = t.pnl() or 0.0
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            else:
                losses += 1
        win_ratio = wins / (wins + losses) if (wins + losses) > 0 else None
        return {"trades": len(self.trades), "wins": wins, "losses": losses, "win_ratio": win_ratio, "total_pnl": total_pnl}

