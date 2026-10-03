import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


import pandas as pd
from db import SessionLocal
from models.indicator import Indicator

def get_momentum_signals(ticker: str, session) -> pd.DataFrame:
    rows =(
        session.query(Indicator)
        .filter(Indicator.ticker == ticker)
        .order_by(Indicator.date)
        .all()
    )

    df = pd.DataFrame([{
        "date": r.date,
        "ma_short": r.ma_short,
        "ma_long": r.ma_long
    }for r in rows])

    # Drop rows where we don't have enough history yet for both MAs
    df = df.dropna(subset=["ma_short","ma_long"])

    # Was short MA above long MA yesterday? Shift(1) looks at the previous row.
    df["short_above_long"] = df["ma_short"] > df["ma_long"]
    df["prev_short_above_long"] = df["short_above_long"].shift(1)

    def determine_signal(row):
        if pd.isna(row["prev_short_above_long"]):
            return "HOLD"
        if row["short_above_long"] and not row["prev_short_above_long"]:
            return "BUY"   # just crossed up
        if not row["short_above_long"] and row["prev_short_above_long"]:
            return "SELL"  # just crossed down
        return "HOLD"      # no change in relationship

    df["signal"] = df.apply(determine_signal, axis=1)

    df["confidence"] = ((df["ma_short"] - df["ma_long"]).abs() / df["ma_long"])

    return df[["date", "ma_short", "ma_long", "signal", "confidence"]]
    

if __name__ == "__main__":
    session = SessionLocal()
    result = get_momentum_signals("AAPL", session)
    print(result[result["signal"] != "HOLD"])  # only show actual BUY/SELL days
    session.close()