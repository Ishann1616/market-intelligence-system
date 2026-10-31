import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from models.price import Price
from backtest.agent_states import get_agent_states

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()
    out = []
    for t in TICKERS:
        s = get_agent_states(t, session, get_price_df(t, session))
        out.append({
            "ticker": t,
            "days": len(s),
            "start": s["date"].min(),
            "mom_in_%": round(s["mom"].mean()*100, 1),
            "mr_in_%": round(s["mr"].mean()*100, 1),
            "agree_%": round((s["mom"] == s["mr"]).mean() * 100, 1),
            "corr": round(s["mom"].corr(s["mr"]), 3),
        })
        if t == "AAPL":
            print(s.tail(8).to_string(index=False))
    print(pd.DataFrame(out).to_string(index=False))
    session.close()


if __name__ == "__main__":
    main()