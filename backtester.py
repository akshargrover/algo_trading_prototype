import pandas as pd

def backtest(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    trades = []
    in_trade = False
    entry_price = 0
    for idx, row in df.iterrows():
        if row['buy_signal'] and not in_trade:
            entry_price = row['Close']
            entry_date = row['Date']
            in_trade = True
        elif in_trade and row['rsi'] > 70:
            exit_price = row['Close']
            exit_date = row['Date']
            pnl = exit_price - entry_price
            trades.append({
                'Ticker': ticker,
                'Entry Date': entry_date,
                'Exit Date': exit_date,
                'Entry': entry_price,
                'Exit': exit_price,
                'PnL': pnl
            })
            in_trade = False
    return pd.DataFrame(trades)
