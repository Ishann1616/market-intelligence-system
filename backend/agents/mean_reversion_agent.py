import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from models.indicator import Indicator

def get_mean_reversion_signals(ticker: str, session) -> pd.DataFrame:
    rows = (
        session.query(Indicator)
        .filter(Indicator.ticker == ticker)
        .order_by(Indicator.date)
        .all()
    )

    df = pd.DataFrame([{
        "date": r.date,
        "rsi": r.rsi
    } for r in rows])

    df = df.dropna(subset=["rsi"])

    def determine_signal(rsi_value):
        if rsi_value < 30:
            return "BUY"
        if rsi_value > 70:
            return "SELL"
        return "HOLD"

    df["signal"] = df["rsi"].apply(determine_signal)

     # Confidence = how far RSI is from the neutral midpoint (50), scaled 0-1
    df["confidence"] = (df["rsi"] - 50).abs() / 50
    df["confidence"] = df["confidence"].round(4)

    return df[["date", "rsi", "signal", "confidence"]]


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 200)

    session = SessionLocal()
    result = get_mean_reversion_signals("AAPL", session)
    signals_only = result[result["signal"] != "HOLD"]
    print(signals_only.head(20).to_string())
    print("\nBUY count:", (result["signal"] == "BUY").sum())
    print("SELL count:", (result["signal"] == "SELL").sum())
    session.close()