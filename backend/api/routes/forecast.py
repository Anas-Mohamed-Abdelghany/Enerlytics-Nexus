from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
from core.services.forecast_service import generate_lstm_forecast
from models.schemas import OHLCVPoint

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def get_forecast(
    market: str = Body("US‑TEXAS", description="Market identifier"),
    horizon_days: int = Body(30, description="Forecast horizon in days"),
    prediction_type: str = Body("regression", description="'regression' or 'classification'"),
    architecture: str = Body("bidirectional", description="Neural architecture: 'standard', 'bidirectional', or 'pretrained'"),
    check_samples: int = Body(5, description="Number of robustness check samples"),
    series: List[OHLCVPoint] = Body(..., description="Historical OHLCV data to train LSTM")
):
    """
    Return an LSTM-based price forecast trained on the provided historical series.
    WARNING: Training occurs synchronously and may take a few seconds.
    """
    try:
        return generate_lstm_forecast(
            market=market, 
            series=series, 
            horizon_days=horizon_days,
            prediction_type=prediction_type,
            architecture=architecture,
            check_samples=check_samples
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

