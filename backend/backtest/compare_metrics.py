import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from models.price import Price
from agents.momentum_agent import get_momentum_signals
from agents.mean_reversion_agent import get_mean_reversion_signals
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics


TICKER = "AAPL"
STARTING_CAPITAL = 10000

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()

    prices = get_price_df(TICKER, session)
    momentum_signals = get_momentum_signals(TICKER, session)
    mean_rev_signals = get_mean_reversion_signals(TICKER, session)

    # Common start = the latest "first valid day" among the strategies
    common_start = max(momentum_signals["date"].min(), mean_rev_signals["date"].min())
    print(f"Common start date for all strategies: {common_start}")

    # Trim everything to begin on the same day
    prices = prices[prices["date"] >= common_start].reset_index(drop=True)
    momentum_signals = momentum_signals[momentum_signals["date"] >= common_start]
    mean_rev_signals = mean_rev_signals[mean_rev_signals["date"] >= common_start]

    mom_result = run_backtest(momentum_signals, prices, STARTING_CAPITAL)
    mr_result = run_backtest(mean_rev_signals, prices, STARTING_CAPITAL)

    # Buy-and-hold from the same start date
    shares = STARTING_CAPITAL / prices["close"].iloc[0]
    buy_hold_values = prices["close"] * shares

    table = pd.DataFrame({
        "Buy & Hold": compute_metrics(buy_hold_values),
        "Momentum": compute_metrics(mom_result["portfolio_value"]),
        "Mean-Reversion": compute_metrics(mr_result["portfolio_value"]),
    }).T

    print(f"\n{TICKER} metrics (same start date, ${STARTING_CAPITAL:,} start, 0.1% cost per trade):\n")
    print(table.to_string())

    session.close()

if __name__ == "__main__":
    main()