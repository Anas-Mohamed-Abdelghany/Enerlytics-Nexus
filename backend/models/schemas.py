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
    
    # Energy specific fields
    battery_p: Optional[float] = Field(None, description="Battery power (kW)")
    grid_p:    Optional[float] = Field(None, description="Grid power (kW)")
    load_p:    Optional[float] = Field(None, description="Load power (kW)")
    pv_p:      Optional[float] = Field(None, description="PV power (kW)")
    selling_price: Optional[float] = Field(None, description="Selling price (EUR/kWh)")

    is_forecast: Optional[bool] = Field(False)
    lower_ci:  Optional[float] = Field(None)
    upper_ci:  Optional[float] = Field(None)
    soc_reconstructed: Optional[float] = Field(None)
    integrity_flags: List[str] = Field(default_factory=list)


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
    shap_metadata: Optional[dict] = Field(None)
    battery_simulation: Optional[dict] = Field(None)
    horizon_sensitivity: Optional[list] = Field(None)

class ForecastRequest(BaseModel):
    market: str
    horizon_days: int = 30
    series: List[OHLCVPoint]
    prediction_type: str = "regression"
    architecture: str = "bidirectional"
    check_samples: int = 5

# ─── Battery Optimizer ────────────────────────────────────────────────────────

class BatteryOptimizationRequest(BaseModel):
    price_forecast: List[float]
    sell_price_forecast: Optional[List[float]] = None
    load_forecast: List[float]
    solar_forecast: List[float]
    soc_init: Optional[float] = 0.5
    battery_capacity_kwh: Optional[float] = 16.0
    p_max_kw: Optional[float] = 8.0
    grid_limit_kw: Optional[float] = 6.0
    horizon_steps: Optional[int] = 96

class BatteryOptimizationResponse(BaseModel):
    status: str
    soc_trajectory: List[float]
    charge_schedule: List[float]
    discharge_schedule: List[float]
    grid_import: List[float]
    grid_export: List[float]
    total_cost_eur: float
    baseline_cost_eur: float
    savings_eur: float
    savings_pct: float
    timestamps: Optional[List[datetime]] = None

