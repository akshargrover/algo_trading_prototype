import pandas as pd
import ta

def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['20dma'] = df['Close'].rolling(window=20).mean()
    df['50dma'] = df['Close'].rolling(window=50).mean()
    df['dma_signal'] = (df['20dma'] > df['50dma']) & (df['20dma'].shift(1) <= df['50dma'].shift(1))
    df['buy_signal'] = (df['rsi'] < 30) & df['dma_signal']
    return df