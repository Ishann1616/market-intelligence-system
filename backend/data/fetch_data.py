import yfinance as yf
import pandas as pd
import os

TICKERS =["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]
PERIOD = "5y"

def fetch_stock_data(ticker: str)-> pd.DataFrame:
    print(f"Fetching {ticker}....")
    df = yf.download(ticker, period=PERIOD, interval="1d")
    df["ticker"]= ticker
    return df

def main():
    os.makedirs("raw_data",exist_ok=True)

    all_data = []
    for ticker in TICKERS:
        df= fetch_stock_data(ticker)
        df.to_csv(ticker)
        df.to_csv(f"raw_data/{ticker}.csv ")
        all_data.append(df)
        print(f"Saved {ticker}: {len(df)} rows")

    combined = pd.concat(all_data)
    combined.to_csv("raw_data/all_tickers.csv")
    print(f"\nDone. Total rows: {len(combined)}")

if __name__ == "__main__":
    main()