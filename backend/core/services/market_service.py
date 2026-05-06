"""
Market Service — Data layer for historical price retrieval.

TODO for engineers:
  Replace the stub below with real data sources, for example:
    - EIA Open Data API  (https://www.eia.gov/opendata/)
    - ERCOT settlement point prices
    - A custom Pandas / PyTorch pipeline loaded from a file store
  The function signature and PriceData return schema must remain unchanged
  so the existing route & frontend integration keep working.
"""

from datetime import datetime
from typing import List
from models.schemas import PriceData, PricePoint


def get_historical_prices(
    market: str = "US-TEXAS",
    timeframe: str = "1M",
    interval: str = "1D",
) -> PriceData:
    """
    Return historical OHLCV price data for the requested market.

    Currently returns an empty series (no simulation).
    Wire up a real data source here when ready.

    Args:
        market:    Market identifier, e.g. "US-TEXAS".
        timeframe: Lookback window, e.g. "1W" | "1M" | "3M" | "6M" | "1Y" | "ALL".
        interval:  Candle interval,  e.g. "1H" | "1D" | "1W".

    Returns:
        PriceData with an empty series until a real source is connected.
    """
    # ── Plug real data-fetching logic here ──────────────────────────────────
    # Example structure for each candle:
    #
    #   PricePoint(
    #       timestamp = datetime(...),
    #       price     = 42.50,   # close (legacy field)
    #       open      = 41.00,
    #       high      = 43.00,
    #       low       = 40.50,
    #       close     = 42.50,
    #       volume    = 1500.0,
    #   )
    # ────────────────────────────────────────────────────────────────────────

    series: List[PricePoint] = []

    return PriceData(market=market, series=series)
