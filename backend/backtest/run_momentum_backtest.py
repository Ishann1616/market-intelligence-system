import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import SessionLocal
from models.price import Price
from agents.momentum_agent import get_momentum_signals
from backtest.engine import run_backtesting
import pandas as pd

TICKER = "AAPL"

def get_price_df(tickers, session):
    rows = session.query(Price).filter(Price.ticker == tickers).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()
    signals = get_momentum_signals(TICKER, session)
    prices = get_price_df(TICKER, session)

    result = run_backtesting(signals, prices, starting_capital=10000)

    print(result.tail(10).to_string())
    print(f"\nStarting capital: $10,000")
    print(f"Final portfolio value: ${result['portfolio_value'].iloc[-1]:,.2f}")

    session.close()

if __name__ == "__main__":
    main()