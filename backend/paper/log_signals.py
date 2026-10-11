import sys
import os
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "signal_log.csv")

def fetch_closes(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    close = df["Close"].squeeze()
    close.index = pd.to_datetime(close.index).date
    return close

def drop_unfinished_bar(close):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    if close.index[-1] == now_et.date() and (now_et.hour, now_et.minute) < (16, 15):
        return close.iloc[:-1]
    return close

def compute_indicators(close):
    df = pd.DataFrame({"close": close})
    df["ma_short"] = df["close"].rolling(20).mean()
    df["ma_long"] = df["close"].rolling(50).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["rsi"] = 100 - 100 / (1 + rs)
    return df

def momentum_signal(df):
    above = df["ma_short"] > df["ma_long"]
    today, yesterday = above.iloc[-1], above.iloc[-2]
    last = df.iloc[-1]
    if today and not yesterday:
        signal = "BUY"
    elif not today and yesterday:
        signal = "SELL"
    else:
        signal = "HOLD"
    confidence = round(abs(last["ma_short"] - last["ma_long"]) / last["ma_long"], 4)
    return signal, confidence

def mean_reversion_signal(df):
    rsi = df["rsi"].iloc[-1]
    signal = "BUY" if rsi < 30 else "SELL" if rsi > 70 else "HOLD"
    confidence = round(abs(rsi - 50) / 50, 4)
    return signal, confidence

def verify():
    # One-time check: should match the values already stored in your database
    df = compute_indicators(fetch_closes("AAPL"))
    row = df.loc[date(2026, 9, 25)]
    print("ma_short:", row["ma_short"], "(database: 329.39600067138673)")
    print("ma_long: ", row["ma_long"], "(database: 321.74280212402346)")
    print("rsi:     ", row["rsi"], "(database: 74.39873469091043)")

def main():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.exists(LOG_PATH)
    seen = set()
    if file_exists:
        old = pd.read_csv(LOG_PATH)
        seen = set(zip(old["signal_date"].astype(str), old["ticker"], old["agent"]))

    logged_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_rows = []

    for ticker in TICKERS:
        close = drop_unfinished_bar(fetch_closes(ticker))
        df = compute_indicators(close)
        signal_date = str(close.index[-1])
        price = round(float(close.iloc[-1]), 2)

        for agent, fn in [("momentum", momentum_signal), ("mean_reversion", mean_reversion_signal)]:
            if (signal_date, ticker, agent) in seen:
                continue
            signal, confidence = fn(df)
            new_rows.append({
                "signal_date": signal_date, "ticker": ticker, "agent": agent,
                "signal": signal, "confidence": confidence,
                "close": price, "logged_at_utc": logged_at,
            })

    if new_rows:
        pd.DataFrame(new_rows).to_csv(LOG_PATH, mode="a", header=not file_exists, index=False)
        print(f"Logged {len(new_rows)} new rows")
        print(pd.DataFrame(new_rows).to_string(index=False))
    else:
        print("Nothing new to log (already up to date)")

if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()