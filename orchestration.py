from typing import List, Optional
from data_fetcher import DataFetcher
from config import LOG
from strategy import Strategy, Trade
from backtester import Backtester
import pandas as pd
from ml_model import MLModel
from logging import GSheetsLogger, GSHEETS_AVAILABLE

def run_backtest_for_tickers(tickers: List[str], period: str = "6mo") -> dict:
    fetcher = DataFetcher(tickers=tickers, period=period)
    all_data = fetcher.fetch()
    results = {}
    for t, df in all_data.items():
        LOG.info(f"Preparing signals for {t}")
        strat = Strategy(df)
        signals = strat.generate_signals()
        bt = Backtester(signals_df=signals, ticker=t)
        trades, final_value = bt.run()
        summary = bt.summary()
        results[t] = {"trades": trades, "final_value": final_value, "summary": summary}
    return results


def run_ml_for_ticker(df: pd.DataFrame, model_type: str = "tree") -> dict:
    strat = Strategy(df)
    signals = strat.generate_signals()
    df_signals = signals
    ml = MLModel(df_signals)
    try:
        model, acc = ml.train(model_type=model_type)
    except Exception as e:
        LOG.exception("ML training failed")
        return {"success": False, "error": str(e)}
    return {"success": True, "accuracy": acc}


def scan_and_log(tickers: List[str], gsheet: Optional[GSheetsLogger] = None):
    fetcher = DataFetcher(tickers=tickers, period="6mo")
    all_data = fetcher.fetch(force_refresh=True)
    aggregated_trades = []
    aggregated_summary = {}
    for t, df in all_data.items():
        strat = Strategy(df)
        signals = strat.generate_signals()
        latest = signals.iloc[-1]
        if latest.get("buy_signal", False):
            LOG.info(f"{t}: BUY signal detected on {signals.index[-1].date()}")
            aggregated_trades.append(Trade(ticker=t, entry_date=signals.index[-1].date(), entry_price=latest["Close"]))
        # For the purpose of logging, create a per-ticker summary
        bt = Backtester(signals_df=signals, ticker=t)
        trades, final_val = bt.run()
        aggregated_summary[t] = bt.summary()
    if gsheet and GSHEETS_AVAILABLE:
        # flatten trades into single list and push
        gsheet.write_trade_log(aggregated_trades, tab_name="trade_log")
        gsheet.write_summary({k: str(v) for k, v in aggregated_summary.items()}, tab_name="summary")
    return aggregated_trades, aggregated_summary
