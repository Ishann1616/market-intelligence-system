from sqlalchemy import Column, Integer, String, Float, Date
from models.price import Base

class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    ma_short = Column(Float)
    ma_long = Column(Float)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)

    