import pandas as pd
import sys
import os 

# Allow importing from the backend/ root (db.py, models/) since this file lives in backend/data/
sys.path.append(os.path.join(os.path.dirname(__file__),".."))

from db import SessionLocal
from models.price import Price

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]

def load_ticker_to_db(ticker:str, session):
    filepath =f"raw_data/{ticker}.csv"
    df= pd.read_csv(filepath)

    
    # yfinance's CSV has some extra header rows we don't need — skip if present
    df = df[pd.to_datetime(df.iloc[:, 0], format="%Y-%m-%d", errors="coerce").notna()]

    count = 0
    for _, row in df.iterrows():
        price_row = Price(
            ticker=ticker,
            date=pd.to_datetime(row.iloc[0], format="%Y-%m-%d").date(),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"]),
        )
        session.add(price_row)
        count += 1

    print(f"Loaded {count} rows for {ticker}")

def main():
    session = SessionLocal()
    try:
        for ticker in TICKERS:
            load_ticker_to_db(ticker, session)
        session.commit()
        print("\nALl data committed to database")
    except Exception as e:
        session.rollback()
        print(f"Error occured, rolled back: {e}")
    finally:
        session.close()

if __name__== "__main__":
    main()
