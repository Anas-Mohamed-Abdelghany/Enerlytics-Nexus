"""
Resample route — POST /api/resample/
Accepts a full OHLCV series + timeframe + interval, returns filtered/resampled data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from models.schemas import OHLCVPoint, KPIResponse
from core.services.resample_service import resample_series

router = APIRouter()


class ResampleRequest(BaseModel):
    series:    List[OHLCVPoint] = Field(..., description="Full OHLCV series from upload")
    timeframe: str              = Field("ALL", description="1W | 1M | 3M | 6M | 1Y | ALL")
    interval:  str              = Field("1D",  description="1min | 5min | 15min | 30min | 1H | 4H | 1D | 1W | 1M")


class ResampleResponse(BaseModel):
    timeframe: str
    interval:  str
    rows:      int
    series:    List[OHLCVPoint]
    kpis:      KPIResponse


@router.post("/", response_model=ResampleResponse, summary="Filter and resample an OHLCV series")
async def resample(req: ResampleRequest):
    """
    Given the full OHLCV series returned by /api/upload/, apply:
    - **Timeframe filter**: keep only candles within the lookback window.
    - **Interval resampling**: aggregate to the requested candle size.

    Returns the resampled series and updated KPIs.
    """
    if not req.series:
        raise HTTPException(status_code=422, detail="Series must not be empty.")

    try:
        resampled, kpis = resample_series(req.series, req.timeframe, req.interval)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return ResampleResponse(
        timeframe=req.timeframe,
        interval=req.interval,
        rows=len(resampled),
        series=resampled,
        kpis=kpis,
    )
