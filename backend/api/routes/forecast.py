from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
from datetime import datetime
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
        # Route based on architecture preference
        if architecture in ["lightgbm", "advanced"]:
            print(f"🚀 Routing to LightGBM Forecaster (Horizon: {horizon_days} days)")
            from core.services.energy_forecaster import forecaster, predict_forecast
            import pandas as pd
            
            # Map Close/Solar if needed for the energy engine
            df = pd.DataFrame([p.model_dump() for p in series])
            if 'close' in df.columns and 'load' not in df.columns:
                df['load'] = df['close']
            if 'pv_p' in df.columns and 'solar' not in df.columns:
                df['solar'] = df['pv_p']
            
            # Use the high-precision predict logic
            try:
                await forecaster.train_pipeline(df) 
                print("✅ Training complete, starting prediction...")
                
                pred_res = await predict_forecast({
                    "hours_ahead": horizon_days * 24, 
                    "historical_data": df.to_dict('records')
                })
                
                # Map to ForecastPoint objects with timestamps
                from datetime import timedelta
                # Use the last timestamp from the input series
                last_ts_val = series[-1].timestamp / 1000.0 if not df.empty else datetime.now().timestamp()
                last_ts = datetime.fromtimestamp(last_ts_val)
                
                points = []
                load_preds = pred_res.get("load_forecast", [])
                for i, val in enumerate(load_preds):
                    points.append({
                        "timestamp": (last_ts + timedelta(minutes=15 * (i+1))).isoformat(),
                        "forecast": float(val),
                        "lower_ci": float(pred_res.get("load_lower", [0]*len(load_preds))[i]),
                        "upper_ci": float(pred_res.get("load_upper", [0]*len(load_preds))[i])
                    })
                
                print(f"✨ Prediction successful: {len(points)} points generated.")
                return {
                    "type": "regression",
                    "market": market,
                    "horizon_hours": horizon_days * 24,
                    "points": points,
                    "source": "LightGBM"
                }
            except Exception as inner_e:
                print(f"❌ LightGBM Prediction Error: {inner_e}")
                import traceback
                traceback.print_exc()
                raise inner_e
            
        return generate_lstm_forecast(
            market=market, 
            series=series, 
            horizon_days=horizon_days,
            prediction_type=prediction_type,
            architecture=architecture,
            check_samples=check_samples
        )
    except Exception as e:
        print(f"❌ Forecast Route Exception: {e}")
        raise HTTPException(status_code=400, detail=str(e))

