# Algo-Trading Prototype

This is a modular Python project for running a basic algo-trading system based on RSI and MA crossover, with logging to Google Sheets and optional ML prediction.

## Features
- Fetch stock data (INFY, TCS, RELIANCE)
- Apply technical indicators (RSI, 20/50 DMA)
- Generate buy signals & backtest
- Log trades and analytics in Google Sheets
- ML model for next-day direction prediction

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Add your Google API `creds.json`
3. Create a Google Sheet titled `AlgoTrade Log`
4. Run the main script: `python main.py`
