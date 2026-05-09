import os
import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException

from core.services.lstm_forecaster import generate_lstm_forecast_logic as generate_lstm_forecast
from core.services.advanced_forecaster import AdvancedForecaster
from models.schemas import OHLCVPoint, ForecastRequest, ForecastResponse

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])

# Instance for advanced logic
advanced_forecaster = AdvancedForecaster()

@router.post("/")
async def get_forecast_unified(req: ForecastRequest):
    """
    Backward compatible endpoint that routes to the selected architecture.
    """
    try:
        if req.architecture == "advanced":
            # For the generic market predict route, we map 'close' to 'load'
            data_dicts = [p.model_dump() for p in req.series]
            for d in data_dicts:
                if 'close' in d and 'load' not in d:
                    d['load'] = d['close']
            
            # Simple prediction for now (Advanced is usually energy-focused, but we adapt it)
            res = advanced_forecaster.predict(data_dicts, req.horizon_days)
            if "error" in res:
                # If not trained, attempt to train on the fly for the hackathon demo
                df = pd.DataFrame(data_dicts)
                await advanced_forecaster.train_pipeline(df)
                res = advanced_forecaster.predict(data_dicts, req.horizon_days)
            
            importance = advanced_forecaster.get_shap().get("top_10_importance", {})
            
            return {
                "type": "regression",
                "market": req.market,
                "horizon_hours": req.horizon_days * 24,
                "points": res.get("points", []),
                "feature_importance": importance
            }
        else:
            # Route to LSTM logic
            return generate_lstm_forecast(
                market=req.market,
                series=req.series,
                horizon_days=req.horizon_days,
                prediction_type=req.prediction_type,
                architecture=req.architecture,
                check_samples=req.check_samples
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_forecast(data: List[Dict], architecture: str = "advanced"):
    """
    Triggers training for the selected model.
    """
    try:
        df = pd.DataFrame(data)
        if architecture == "advanced":
            # Map close to load if needed
            if 'close' in df.columns and 'load' not in df.columns:
                df['load'] = df['close']
            return await advanced_forecaster.train_pipeline(df)
        else:
            return {"message": "LSTM training is managed during prediction"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shap")
async def get_shap(architecture: str = "advanced", target: str = "load"):
    if architecture == "advanced":
        return advanced_forecaster.get_shap(target)
    return {"message": "SHAP for LSTM is returned in the main response"}