"""
Resample Service — filters and resamples OHLCV data on the backend.

Given a full list of OHLCVPoints, a timeframe (lookback window)
and an interval (candle size), returns a filtered + aggregated series.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta
from typing import List

import pandas as pd

from models.schemas import OHLCVPoint, KPIResponse


# ─── Maps ────────────────────────────────────────────────────────────────────

TIMEFRAME_DAYS: dict[str, int | None] = {
    "1W":  7,
    "1M":  30,
    "3M":  90,
    "6M":  180,
    "1Y":  365,
    "ALL": None,   # no cutoff
}

INTERVAL_RULE: dict[str, str] = {
    "1MIN":  "1min",
    "5MIN":  "5min",
    "15MIN": "15min",
    "30MIN": "30min",
    "1H":    "1h",
    "4H":    "4h",
    "1D":    "1D",
    "1W":    "1W",
    "1M":    "1ME",   # month-end
    "1Y":    "YE",    # year-end
}


def _compute_kpis(closes: List[float]) -> KPIResponse:
    current  = closes[-1]
    previous = closes[-2] if len(closes) > 1 else current
    change   = current - previous
    change_pct = 0.0 if previous == 0 else (change / previous) * 100
    max_c, min_c = max(closes), min(closes)
    volatility   = 0.0 if min_c == 0 else ((max_c - min_c) / min_c) * 100
    return KPIResponse(
        current=round(current, 4),
        change_pct=round(change_pct, 4),
        is_positive=change >= 0,
        volatility=round(volatility, 4),
        points=len(closes),
    )


def resample_series(
    series:    List[OHLCVPoint],
    timeframe: str = "ALL",
    interval:  str = "1D",
) -> tuple[List[OHLCVPoint], KPIResponse]:
    """
    Filter a series by lookback window and resample to the requested interval.

    Args:
        series:    Full list of OHLCVPoint (sorted ascending by timestamp).
        timeframe: One of 1W | 1M | 3M | 6M | 1Y | ALL.
        interval:  One of 1min | 5min | 15min | 30min | 1H | 4H | 1D | 1W | 1M.

    Returns:
        (resampled_series, kpis) tuple.

    Raises:
        ValueError: If timeframe / interval is unknown or result is empty.
    """
    tf = timeframe.upper()
    iv = interval.upper()

    if tf not in TIMEFRAME_DAYS:
        raise ValueError(
            f"Unknown timeframe '{timeframe}'. "
            f"Choose from: {', '.join(TIMEFRAME_DAYS)}"
        )
    if iv not in INTERVAL_RULE:
        raise ValueError(
            f"Unknown interval '{interval}'. "
            f"Choose from: {', '.join(INTERVAL_RULE)}"
        )

    # Build DataFrame (timestamps are stored as ms)
    df = pd.DataFrame([p.model_dump() for p in series])
    df["dt"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("dt").sort_index()

    # ── Timeframe filter ──────────────────────────────────────────────────
    cutoff_days = TIMEFRAME_DAYS[tf]
    if cutoff_days is not None:
        last_date = df.index.max()
        cutoff = last_date - pd.Timedelta(days=cutoff_days)
        df = df[df.index >= cutoff]

    if df.empty:
        raise ValueError(
            f"No data in the selected timeframe ({timeframe}). "
            "Try a wider window or 'ALL'."
        )

    # ── Resample ──────────────────────────────────────────────────────────
    rule = INTERVAL_RULE[iv]
    ohlcv = df.resample(rule, label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna(subset=["close"])

    if ohlcv.empty:
        raise ValueError(
            f"Resampling to {interval} produced no candles for timeframe {timeframe}."
        )

    # ── Convert back to OHLCVPoint list ──────────────────────────────────
    result: List[OHLCVPoint] = []
    for dt, row in ohlcv.iterrows():
        ts_ms = int(dt.timestamp() * 1000)
        close = float(row["close"])
        result.append(OHLCVPoint(
            timestamp=ts_ms,
            open=  float(row["open"])   if not math.isnan(row["open"])   else close,
            high=  float(row["high"])   if not math.isnan(row["high"])   else close,
            low=   float(row["low"])    if not math.isnan(row["low"])    else close,
            close= close,
            volume=float(row["volume"]) if not math.isnan(row["volume"]) else 0.0,
        ))

    kpis = _compute_kpis([p.close for p in result])
    return result, kpis
