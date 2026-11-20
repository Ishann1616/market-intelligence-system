import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from models.price import Price
from backtest.agent_states import get_agent_states
from backtest.engine_v2 import run_backtest_v2
from backtest.manager import manager_exposure, static_exposure
from backtest.metrics import compute_metrics

TICKER = "AAPL"
LOOKBACK = 30   # pre-registered primary setting


def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()
    prices = get_price_df(TICKER, session)
    states = get_agent_states(TICKER, session, prices)
    session.close()

    p = states[["date", "close"]]
    curves ={
        "Manager": run_backtest_v2(manager_exposure(states, LOOKBACK), p)["portfolio_value"],
        "Static 50/50": run_backtest_v2(static_exposure(states), p)["portfolio_value"],
        "Momentum": run_backtest_v2(states[["date"]].assign(exposure=states["mom"]), p)["portfolio_value"],
        "Mean-Reversion": run_backtest_v2(states[["date"]].assign(exposure=states["mr"]), p)["portfolio_value"],
        "Buy & Hold": states["close"] / states["close"].iloc[0] * 10000, 
    }

    table = pd.DataFrame({k: compute_metrics(v) for k, v in curves.items()}).T
    print(table.to_string())

if __name__ == "__main__":
    main()