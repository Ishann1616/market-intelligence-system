import numpy as np 
import pandas as pd

from db import SessionLocal
from models.price import Price
from agents.momentum_agent import get_momentum_signals
from backtest.engine import run_backtest
from backtest.engine_v2 import run_backtest_v2, signals_to_exposure

TICKER = "AAPL"

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker ==ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()
    signals = get_momentum_signals(TICKER, session)
    prices = get_price_df(TICKER, session)
    session.close()

    old = run_backtest(signals, prices)
    new = run_backtest_v2(signals_to_exposure(signals), prices)

    old_final = old["portfolio_value"].iloc[-1]
    new_final = new["portfolio_value"].iloc[-1]
    print("Rows:", len(old), len(new))
    print("Final old:", round(old_final, 2), " Final new:", round(new_final, 2))
    assert len(old) == len(new)
    assert np.allclose(old["portfolio_value"].values, new["portfolio_value"].values, rtol=1e-9)
    print("CHECK A PASSED: v2 matches v1 on real AAPL momentum signals")


if __name__ == "__main__":
    main()
    
