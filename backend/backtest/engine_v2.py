import pandas as pd 
TRANSACTION_COST_PCT = 0.001

def signals_to_exposure (signal_df: pd.DataFrame) -> pd.DataFrame:
    """BUY -> 1, SELL -> 0, HOLD keeps the previous state. Starts out of the stock."""
    state = 0.0
    exposures = []
    for sig in signal_df["signal"]:
        if sig =="BUY":
            state = 1.0
        elif sig == "SELL":
            state = 0.0
        exposures.append(state) 
    return pd.DataFrame({"date": signal_df["date"].values, "exposure": exposures}) 

def run_backtest_v2(exposure_df: pd.DataFrame, prices_df: pd.DataFrame, starting_capital: float = 10000) -> pd.DataFrame:
    merged = pd.merge(exposure_df[["date", "exposure"]], prices_df[["date", "close"]], on="date", how="inner")
    # Exposure decided at the close of day t is traded at the close of day t+1
    merged["target"] = merged["exposure"].shift(1).fillna(0.0)

    cash = starting_capital
    shares = 0.0
    prev_target = 0.0
    trade_count = 0
    values = []

    for _, row in merged.iterrows():
        price = row["close"]
        target = row["target"]

        if abs(target - prev_target)> 1e-12:
            value = cash + shares * price
            traded = abs(target * value - shares * price)   # money moved
            cost = traded * TRANSACTION_COST_PCT
            value_after = value - cost
            shares = target * value_after / price
            cash = value_after - shares * price
            prev_target = target
            trade_count += 1

        values.append(cash + shares * price)

    merged["portfolio_value"] = values
    print(f"Total trades executed: {trade_count}")
    return merged[["date", "close", "target", "portfolio_value"]]