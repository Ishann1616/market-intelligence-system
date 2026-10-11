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

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]
STARTING_CAPITAL = 10000

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def build_curves(ticker, session):
    prices = get_price_df(ticker, session)
    momentum_signals = get_momentum_signals(ticker, session)
    mean_rev_signals = get_mean_reversion_signals(ticker, session)

    common_start = max(momentum_signals["date"].min(), mean_rev_signals["date"].min())

    prices = prices[prices["date"] >= common_start].reset_index(drop=True)
    momentum_signals = momentum_signals[momentum_signals["date"] >= common_start]
    mean_rev_signals = mean_rev_signals[mean_rev_signals["date"] >= common_start]

    mom_result = run_backtest(momentum_signals, prices, STARTING_CAPITAL)
    mr_result = run_backtest(mean_rev_signals, prices, STARTING_CAPITAL)

    shares = STARTING_CAPITAL / prices["close"].iloc[0]

    return {
        "Buy & Hold": prices["close"] * shares,
        "Momentum": mom_result["portfolio_value"],
        "Mean-Reversion": mr_result["portfolio_value"],
    }

def analyze_ticker(ticker, session):
    curves = build_curves(ticker, session)
    return pd.DataFrame({name: compute_metrics(v) for name , v in curves.items()}).T

def main():
    session = SessionLocal()
    sharpe_summary = {}
    return_summary = {}

    for ticker in TICKERS:
        table = analyze_ticker(ticker, session)
        print(f"\n===== {ticker} =====")
        print(table.to_string())
        sharpe_summary[ticker] = table["sharpe"]
        return_summary[ticker] = table["total_return_pct"]

    print("\n\n===== SUMMARY: Sharpe ratio =====")
    print(pd.DataFrame(sharpe_summary).T.to_string())
    print("\n===== SUMMARY: Total return % =====")
    print(pd.DataFrame(return_summary).T.to_string())

    session.close()

if __name__ == "__main__":
    main()