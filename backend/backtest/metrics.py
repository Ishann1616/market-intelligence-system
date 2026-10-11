import numpy as np 
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

def compute_metrics(portfolio_values: pd.Series) -> dict:
    """
     portfolio_values: daily portfolio value, one number per trading day, in date order.
    """
    values = portfolio_values.reset_index(drop = True)

    # Daily return = today's value vs yesterday's, as a fraction
    daily_returns = values.pct_change().dropna()

    # Annualized return: total growth, scaled to a 1-year equivalent
    total_return = values.iloc[-1]/values.iloc[0]
    n_days = len(values)
    annualized_return = total_return ** (TRADING_DAYS_PER_YEAR)

    # Annualized volatility: daily std dev, scaled up to a year
    annualized_vol = daily_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    # Sharpe ratio (risk-free rate assumed 0)
    if daily_returns.std() == 0:
        sharpe = 0.0
    else:
        sharpe = (daily_returns.mean()/daily_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)

    # Max drawdown: worst drop from a previous peak
    running_peak = values.cummax()
    drawdown = (values - running_peak)/ running_peak
    max_drawdown = drawdown.min()

    return{
        "total_return_pct": round((total_return-1)*100 ,2),
        "annualized_return_pct": round(annualized_return*100, 2),
        "annualized_vol_pct": round(annualized_vol * 100, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
    }

if __name__ == "__main__":
    # Hand-checkable test: 100 -> 110 -> 90 -> 95
    # Peak is 110, lowest point after is 90, so max drawdown = (90 - 110) / 110 = -18.18%
    test_values = pd.Series([100, 110, 90, 95])
    print(compute_metrics(test_values))






