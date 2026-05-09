import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from models.schemas import PriceData, PricePoint

def get_historical_prices(
    market: str = "BESS-ITALY",
    timeframe: str = "1M",
    interval: str = "1H",
) -> PriceData:
    """
    Returns realistic historical price data for the energy market.
    Includes seasonality and volatility typical of Italian PUN prices.
    """
    # Parse timeframe
    days = 30
    if timeframe == "1W": days = 7
    elif timeframe == "3M": days = 90
    elif timeframe == "1Y": days = 365
    
    # Generate timestamps
    end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=days)
    
    # 1H or 1D intervals
    freq = "H" if interval == "1H" else "D"
    timestamps = pd.date_range(start=start_time, end=end_time, freq=freq)
    
    # Generate Synthetic PUN-like prices (€/MWh)
    # Base: €100
    # Daily seasonality: Peak during day, low at night
    # Weekly seasonality: Lower on weekends
    base_price = 100.0
    
    series: List[PricePoint] = []
    for ts in timestamps:
        hour = ts.hour
        dow = ts.dayofweek
        
        # Seasonality factors
        daily_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (hour - 8) / 24) # Peak at 2pm
        weekly_factor = 0.85 if dow >= 5 else 1.0
        random_factor = np.random.normal(1.0, 0.05)
        
        price = base_price * daily_factor * weekly_factor * random_factor
        
        # Create OHLCV
        vol = 0.02 # 2% volatility for high/low
        series.append(PricePoint(
            timestamp=ts,
            price=round(float(price), 2),
            open=round(float(price * (1 + np.random.uniform(-0.01, 0.01))), 2),
            high=round(float(price * (1 + vol)), 2),
            low=round(float(price * (1 - vol)), 2),
            close=round(float(price), 2),
            volume=float(np.random.randint(1000, 5000))
        ))
        
    return PriceData(market=market, series=series)
