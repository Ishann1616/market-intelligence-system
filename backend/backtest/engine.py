import pandas as pd

TRANSACTION_COST_PCT = 0.001 # 0.1% per trade — covers fees + slippage

def run_backtesting(signal_df: pd.DataFrame, prices_df: pd.DataFrame, starting_capital: float = 10000) -> pd.DataFrame:
    merged = pd.merge(signal_df[["date", "signal"]], prices_df[["date", "close"]], on="date", how="inner")
    merged = merged.sort_values("date").reset_index(drop=True)

    cash = starting_capital
    shares = 0.0
    portfolio_values =[]
    trade_count = 0 

    for _, row in merged.iterrows():
        price = row["close"]
        signal = row["signal"]

        if signal =="BUY" and shares == 0:
            # Go all-in: convert all cash into shares at today's price
            cost = cash * TRANSACTION_COST_PCT
            cash_after_cost = cash - cost
            shares = cash_after_cost/price
            cash = 0.0
            trade_count += 1


        elif signal == "SELL" and shares > 0:
            # Go all-out: convert all shares back into cash at today's price
            proceeds = shares * price
            cost = proceeds * TRANSACTION_COST_PCT
            cash = proceeds - cost
            shares = 0.0
            trade_count +=1

        # Whether we traded today or not, record today's total portfolio value
        total_value = cash +(shares * price)
        portfolio_values.append(total_value)

    merged["portfolio_value"] = portfolio_values
    print(f"Total trades executed: {trade_count}")
    return merged[["date", "close", "signal", "portfolio_value"]]


