from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ─── Upload / OHLCV ───────────────────────────────────────────────────────────

class OHLCVPoint(BaseModel):
    """Single normalised OHLCV candle returned after file upload."""
    timestamp: float = Field(..., description="Unix timestamp in milliseconds")
    open:      float = Field(..., description="Open price")
    high:      float = Field(..., description="High price")
    low:       float = Field(..., description="Low price")
    close:     float = Field(..., description="Close price")
    volume:    float = Field(0.0,  description="Volume")
    is_forecast: Optional[bool] = Field(False)
    lower_ci:  Optional[float] = Field(None)
    upper_ci:  Optional[float] = Field(None)


class KPIResponse(BaseModel):
    current:    float = Field(..., description="Last close price")
    change_pct: float = Field(..., description="% change from previous close")
    is_positive: bool = Field(..., description="Whether the change is >= 0")
    volatility:  float = Field(..., description="(max-min)/min * 100")
    points:      int   = Field(..., description="Total number of candles")


class UploadResponse(BaseModel):
    filename:   str              = Field(..., description="Original filename")
    rows:       int              = Field(..., description="Number of valid candles")
    series:     List[OHLCVPoint] = Field(..., description="Normalised OHLCV series")
    kpis:       KPIResponse      = Field(..., description="Computed KPIs")


# ─── Legacy price schema (used by market route) ───────────────────────────────

class PricePoint(BaseModel):
    timestamp: datetime = Field(..., description="ISO-8601 timestamp")
    price:     float    = Field(..., ge=0, description="Close price (legacy)")
    open:      Optional[float] = Field(None)
    high:      Optional[float] = Field(None)
    low:       Optional[float] = Field(None)
    close:     Optional[float] = Field(None)
    volume:    Optional[float] = Field(None)


class PriceData(BaseModel):
    market: str              = Field(..., description="Market identifier")
    series: List[PricePoint] = Field(..., description="Chronological price series")


# ─── Forecast ─────────────────────────────────────────────────────────────────

class ForecastPoint(BaseModel):
    timestamp: datetime      = Field(..., description="Future timestamp")
    forecast:  float         = Field(..., description="Predicted price")
    lower_ci:  Optional[float] = Field(None)
    upper_ci:  Optional[float] = Field(None)


class ForecastResponse(BaseModel):
    type:         str               = Field("regression", description="regression or classification")
    market:       str               = Field(...)
    horizon_hours: int              = Field(..., ge=1)
    points:       Optional[List[ForecastPoint]] = Field(None)
    prediction:   Optional[str]     = Field(None, description="UP, DOWN, or STABLE (for classification)")
    feature_importance: Optional[dict] = Field(None, description="XAI feature importance scores")

