from fastapi import FastAPI, HTTPException, Query

from api.signals import router as signals_router
from db import SessionLocal
from models.price import Price

from api.backtest import router as backtest_router
from api.results import router as results_router

app = FastAPI(title="Market Intelligence API")
app.include_router(signals_router)
app.include_router(backtest_router)
app.include_router(results_router)

TICKERS = ["AAPL", "TSLA", "JPM", "KO", "NVDA", "MSFT"]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickers")
def tickers():
    return TICKERS


@app.get("/prices/{ticker}")
def prices(ticker: str, limit: int = Query(250, ge=1, le=5000)):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker {ticker}")
    session = SessionLocal()
    try:
        rows = (
            session.query(Price)
            .filter(Price.ticker == ticker)
            .order_by(Price.date.desc())
            .limit(limit)
            .all()
        )
    finally:
        session.close()
    rows.reverse()
    return [{"date": str(r.date), "close": r.close, "volume": r.volume} for r in rows]