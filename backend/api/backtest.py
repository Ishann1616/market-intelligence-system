from fastapi import APIRouter, HTTPException

from backtest.agent_states import get_agent_states
from backtest.manager import manager_exposure, static_exposure
from backtest.run_manager_all import LOOKBACK, TICKERS, curve, get_price_df
from db import SessionLocal

router = APIRouter()

START_CAPITAL = 10000

@router.get("/backtest/{ticker}")
def backtest(ticker:str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker {ticker}")

    session = SessionLocal()
    try: 
        states = get_agent_states(ticker, session, get_price_df(ticker, session))
    finally:
        session.close()

    p = states[["date", "close"]]
    curves ={
        "Manager": curve(manager_exposure(states, LOOKBACK), p),
        "Static 50/50": curve(static_exposure(states), p),
        "Momentum": curve(states[["date"]].assign(exposure=states["mom"]), p),
        "Mean-Reversion": curve(states[["date"]].assign(exposure=states["mr"]), p),
        "Buy & Hold": states["close"]/states["close"].iloc[0]*START_CAPITAL,
    }

    n = len(states)
    out ={}
    for name, values in curves.items():
        series = [round(float(v),2) for v in values]
        if len(series) != n:
            raise HTTPException(
                status_code=500,
                detail=f"{name} has {len(series)} points, expected {n}",
            )
        out[name] = series

    return{
       "ticker": ticker,
        "lookback": LOOKBACK,
        "dates": [str(d) for d in states["date"]],
        "curves": out, 
    }
