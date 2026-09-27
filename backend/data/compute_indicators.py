import sys
import os 
sys.path.append(os.path.join(os.path.dirname(__file__),".."))

import pandas as pd
from db import SessionLocal
from models.price import Price
from models.indicator import Indicator

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]

def compute_indicators_for_ticker(ticker: str, session):
    # Pull this ticker's price rows from the DB, ordered by date — order is critical
    prices=(
        session.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.date)
        .all()
    )

    df = pd.DataFrame([{
        "date": p.date,
        "close": p.close
    } for p in prices])
    

    # --- Moving Averages ---
    df["ma_short"] = df["close"].rolling(window=20).mean()
    df["ma_long"] = df["close"].rolling(window=50).mean()

    # --- RSI (14-day) ---
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain/avg_loss
    df["rsi"] = 100 - (100/(1+rs))

    # --- MACD ---
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    count =0
    for _, row in df.iterrows():
        indicator_row = Indicator(
            ticker=ticker,
            date=row["date"],
            ma_short=row["ma_short"] if pd.notna(row["ma_short"]) else None,
            ma_long=row["ma_long"] if pd.notna(row["ma_long"]) else None,
            rsi=row["rsi"] if pd.notna(row["rsi"]) else None,
            macd=row["macd"] if pd.notna(row["macd"]) else None,
            macd_signal=row["macd_signal"] if pd.notna(row["macd_signal"]) else None,
        )
        session.add(indicator_row)
        count += 1

    print(f"Computed indicators for {ticker}: {count} rows")

def main():
    session = SessionLocal()
    try:
        for ticker in TICKERS:
            compute_indicators_for_ticker(ticker, session)
        session.commit()
        print("\nAll indicators committed to database.")
    except Exception as e:
        session.rollback()
        print(f"Error occurred, rolled back: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()