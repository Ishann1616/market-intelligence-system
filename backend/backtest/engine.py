import pandas as pd

def run_backtesting(signal_df: pd.DataFrame, prices_df: pd.DataFrame, starting_capital: float = 10000) -> pd.DataFrame:
    """
    signals_df: must have columns ['date', 'signal'] — one row per trading day
    prices_df: must have columns ['date', 'close']
    """

    # Merge signals with prices on date, so each row has both the signal AND that day's price
    merged = pd.merge(signal_df[["date", "signal"]], prices_df[["date", "close"]], on="date", how="inner")
    merged = merged.sort_values("date").reset_index(drop=True)

    cash = starting_capital
    shares = 0.0
    portfolio_values =[]

    for _, row in merged.iterrows():
        price = row["close"]
        signal = row["signal"]

        if signal =="BUY" and shares == 0:
            # Go all-in: convert all cash into shares at today's price
            shares = cash/price
            cash = 0.0

        elif signal == "SELL" and shares > 0:
            # Go all-out: convert all shares back into cash at today's price
            cash = shares * price
            shares = 0.0

        # Whether we traded today or not, record today's total portfolio value
        total_value = cash +(shares * price)
        portfolio_values.append(total_value)

    merged["portfolio_value"] = portfolio_values
    return merged[["date", "close", "signal", "portfolio_value"]]

