from fastapi import APIRouter, HTTPException
from models.schemas import BatteryOptimizationRequest, BatteryOptimizationResponse, OHLCVPoint
from core.services.battery_optimizer import optimize_battery
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
from typing import Dict, List, Optional
from core.services.energy_forecaster import forecaster
from core.services import lstm_forecaster
import joblib
from core.services.evaluation_service import compute_metrics

router = APIRouter()
MODEL_DIR = "models"

@router.post("/optimize", response_model=BatteryOptimizationResponse)
async def run_battery_optimization(request: BatteryOptimizationRequest):
    """
    Run the LP-based battery optimizer for a given forecast horizon.
    """
    try:
        result = optimize_battery(
            price_forecast=np.array(request.price_forecast),
            load_forecast=np.array(request.load_forecast),
            solar_forecast=np.array(request.solar_forecast),
            soc_init=request.soc_init,
            battery_capacity_kwh=request.battery_capacity_kwh,
            p_max_kw=request.p_max_kw,
            grid_limit_kw=request.grid_limit_kw
        )
        
        if result["status"] == "infeasible":
            raise HTTPException(status_code=400, detail="Optimization problem is infeasible")
            
        # Add synthetic timestamps for the 15-min intervals
        start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        result["timestamps"] = [start_time + timedelta(minutes=15*i) for i in range(len(request.price_forecast))]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate", response_model=BatteryOptimizationResponse)
async def run_rolling_mpc_simulation(request: BatteryOptimizationRequest):
    """
    Simulate a long-term rolling horizon MPC (O(N*LP_solve)).
    """
    try:
        from core.services.battery_optimizer import rolling_mpc_simulation
        result = rolling_mpc_simulation(
            prices=np.array(request.price_forecast),
            loads=np.array(request.load_forecast),
            solars=np.array(request.solar_forecast),
            soc_init=request.soc_init,
            battery_capacity_kwh=request.battery_capacity_kwh or 16.0,
            p_max_kw=request.p_max_kw or 8.0,
            grid_limit_kw=request.grid_limit_kw or 6.0
        )
        
        # Add synthetic timestamps
        start_time = datetime(2025, 1, 1)
        result["timestamps"] = [start_time + timedelta(minutes=15*i) for i in range(len(request.price_forecast))]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/audit")
async def run_audit(request: Dict = None):
    """
    Official 2025 Audit for months 4 (April) and 9 (September).
    Calculates accuracy metrics on the provided historical data.
    """
    data = request.get("data") if request else None
    
    architecture = request.get("architecture", "advanced")
    april_source = request.get("aprilSource", "advanced")
    sept_source = request.get("septSource", "advanced")
    prediction_type = request.get("prediction_type", "regression")

    if not data or len(data) == 0:
        raise HTTPException(status_code=400, detail="No authentic data provided for the Audit. Synthetic fallbacks have been disabled.")

    # Process authentic data
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') if df['timestamp'].dtype == 'int64' else pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # Detect target year: prioritize 2025, fallback to 2024, then most recent
    available_years = df['timestamp'].dt.year.unique()
    target_year = 2025
    if 2025 not in available_years:
        if 2024 in available_years:
            target_year = 2024
        elif len(available_years) > 0:
            target_year = max(available_years)

    results = {}
    overall_errors = []
    overall_actuals = []

    for month_num, month_name in [(4, "April"), (9, "September")]:
        # Filter for target year and the specific month
        month_df = df[(df['timestamp'].dt.year == target_year) & (df['timestamp'].dt.month == month_num)].copy()
        
        if month_df.empty:
            # Fallback: if specific month missing in target year, try ANY month in target year just to show data
            if not df[df['timestamp'].dt.year == target_year].empty:
                month_df = df[df['timestamp'].dt.year == target_year].iloc[:2880].copy()
                display_period = f"Sample {target_year}"
            else:
                results[month_name.lower()] = {
                    "period": f"{month_name} {target_year}",
                    "nrmse": 0, "rmse": 0, "mae": 0, "points": 0, "series": []
                }
                continue
        else:
            display_period = f"{month_name} {target_year}"

        # Determine model file based on architecture
        current_arch = architecture
        if architecture == 'hybrid':
            current_arch = april_source if month_num == 4 else sept_source

        model_file = 'lgbm_load.pkl'
        if current_arch == 'standard': model_file = 'lstm_load_standard.h5'
        elif current_arch == 'bidirectional': model_file = 'lstm_load_bidi.h5'
        elif current_arch == 'advanced':
            # Dynamic Walk-Forward Model Selection for the Web UI
            if month_num == 4 and os.path.exists(os.path.join(MODEL_DIR, 'lgbm_load_april.pkl')):
                model_file = 'lgbm_load_april.pkl'
                forecaster.load_model = joblib.load(os.path.join(MODEL_DIR, model_file))['model']
                forecaster.scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler_april.pkl'))
            elif month_num == 9 and os.path.exists(os.path.join(MODEL_DIR, 'lgbm_load_sept.pkl')):
                model_file = 'lgbm_load_sept.pkl'
                forecaster.load_model = joblib.load(os.path.join(MODEL_DIR, model_file))['model']
                forecaster.scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler_sept.pkl'))
            else:
                if os.path.exists(os.path.join(MODEL_DIR, 'lgbm_load.pkl')):
                    forecaster.load_model = joblib.load(os.path.join(MODEL_DIR, 'lgbm_load.pkl'))['model']
                    forecaster.scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
        elif current_arch == 'lightgbm':
            model_file = 'lgbm_load.pkl'
            if os.path.exists(os.path.join(MODEL_DIR, 'lgbm_load.pkl')):
                forecaster.load_model = joblib.load(os.path.join(MODEL_DIR, 'lgbm_load.pkl'))['model']
                forecaster.scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))

        model_exists = os.path.exists(os.path.join(MODEL_DIR, model_file))
        
        # Display formatting
        if architecture == 'hybrid':
            arch_label = f"Hybrid ({'Walk-Forward' if current_arch == 'advanced' else 'Static'})"
        else:
            arch_label = "LightGBM (Walk-Forward)" if architecture == "advanced" else ("LightGBM" if architecture == "lightgbm" else architecture.upper())
        prediction_source = f"Machine Learning ({arch_label})" if model_exists else f"Baseline Fallback (No {arch_label} Model)"
        
        print(f"Audit {month_name}: Using {prediction_source} (Target: {model_file})")

        # Check if we have a model to generate predictions
        if model_exists:
            try:
                if current_arch in ["advanced", "lightgbm"] and forecaster.load_model:
                    # LightGBM Path
                    feat_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
                    if os.path.exists(feat_path):
                        forecaster.feature_names = joblib.load(feat_path)
                        
                    full_feat_df = forecaster.build_energy_features(df.set_index('timestamp'))
                    month_feat_df = full_feat_df[(full_feat_df.index.year == target_year) & (full_feat_df.index.month == month_num)].copy()
                    
                    if month_feat_df.empty:
                        month_feat_df = forecaster.build_energy_features(month_df.set_index('timestamp'))

                    if not month_feat_df.empty:
                        # Convert back to DataFrame to preserve feature names for LightGBM
                        X_scaled = forecaster.scaler.transform(month_feat_df[forecaster.feature_names])
                        X = pd.DataFrame(X_scaled, columns=forecaster.feature_names)
                        
                        predictions = forecaster.load_model.predict(X)
                        actuals = month_feat_df['load'].values if 'load' in month_feat_df.columns else month_feat_df['load_p'].values
                        timestamps = month_feat_df.index.strftime('%Y-%m-%dT%H:%M:%S').tolist()
                    else:
                        raise ValueError(f"Insufficient data to build features for {month_name}")

                elif architecture in ["standard", "bidirectional"]:
                    # LSTM Path
                    from core.services.lstm_forecaster import predict_lstm_batch
                    predictions = predict_lstm_batch(month_df, architecture=architecture)
                    actuals = month_df['load_p'].values
                    timestamps = month_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist()
                    
                    # LSTM consumes the first 'lookback' (60) rows to make the first prediction
                    # Align actuals and timestamps to the end of the arrays
                    if len(actuals) > len(predictions):
                        actuals = actuals[-len(predictions):]
                        timestamps = timestamps[-len(predictions):]
                    elif len(predictions) > len(actuals):
                        predictions = predictions[-len(actuals):]
                else:
                    raise ValueError(f"Unsupported architecture: {architecture}")
            except Exception as e:
                print(f"Prediction failed for {month_name} ({architecture}): {e}")
                return {"error": f"Audit Failed: {str(e)}. Please ensure your model is trained for {architecture}."}
        else:
            # NO FAKE DATA - Raise error if model missing
            return {"error": f"Model file for '{arch_label}' not found. You must train the model first using the AI Strategy panel or the training script."}

        predictions = np.maximum(0.1, predictions)
        
        # Defensive check against NaNs in raw dataset (causes sklearn metric crash)
        valid_idx = ~np.isnan(actuals) & ~np.isnan(predictions)
        if not np.all(valid_idx):
            actuals = actuals[valid_idx]
            predictions = predictions[valid_idx]
            timestamps = np.array(timestamps)[valid_idx].tolist()
            
        if len(actuals) == 0:
            return {"error": f"Audit Failed: No valid data points remaining for {month_name}."}

        metrics = compute_metrics(actuals, predictions)
        
        overall_errors.extend(np.abs(actuals - predictions))
        overall_actuals.extend(actuals)

        results[month_name.lower()] = {
            "period": display_period,
            "source": prediction_source,
            "nrmse": round(metrics['nrmse'], 2),
            "rmse": round(metrics['rmse'], 3),
            "mae": round(metrics['mae'], 3),
            "points": len(actuals),
            "series": [
                {
                    "ts": timestamps[i],
                    "actual": round(float(actuals[i]), 3),
                    "predicted": round(float(predictions[i]), 3),
                    "delta": round(float(predictions[i] - actuals[i]), 3),
                    "error_pct": round(abs(predictions[i] - actuals[i]) / actuals[i] * 100, 2) if actuals[i] > 0 else 0
                } for i in range(len(actuals))
            ]
        }

    # Calculate overall NRMSE
    if overall_actuals:
        mean_actual = np.mean(overall_actuals)
        rmse = np.sqrt(np.mean(np.array(overall_errors)**2))
        overall_nrmse = round((rmse / mean_actual * 100), 2) if mean_actual > 0 else 0
    else:
        overall_nrmse = 0

    results["overall_nrmse"] = overall_nrmse
    return results

async def _execute_training_pipeline(data: List[Dict], arch_type: str = "all"):
    """
    Internal training engine shared by all specialized endpoints.
    """
    if not data or len(data) == 0:
        raise HTTPException(status_code=400, detail="No training data provided.")
    if not data or len(data) == 0:
        raise HTTPException(status_code=400, detail="No training data provided.")

    df = pd.DataFrame(data)
    
    # Strictly keep only the core 6 columns as requested
    core_cols = ['timestamp', 'load_p', 'pv_p', 'Selling_price_eur_kwh', 'battery_p', 'grid_p']
    df = df[[c for c in core_cols if c in df.columns]]
    
    # Drop any remaining all-NaN columns just in case
    df = df.dropna(axis=1, how='all')
    
    # Filter for load_p or load
    if 'load_p' not in df.columns and 'load' not in df.columns:
         raise HTTPException(status_code=400, detail="Data must contain 'load_p' or 'load' column.")
    
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rows": len(df),
        "steps": [],
        "architectures": {}
    }

    try:
        # 1. LightGBM (Advanced)
        if arch_type in ["all", "lightgbm"]:
            print("\n🚀 Step [1/1]: Initializing LightGBM (Advanced) Training...")
            report["steps"].append("Starting LightGBM (Advanced) training...")
            lgbm_res = await forecaster.train_pipeline(df)
            report["architectures"]["lightgbm"] = {
                "status": "success",
                "rmse": lgbm_res.get("load_rmse"),
                "mae": lgbm_res.get("load_mae")
            }
            print("✅ LightGBM Training Complete.")
            report["steps"].append("LightGBM training complete.")

        # Prepare points for LSTM
        points = []
        for _, row in df.iterrows():
            ts_val = row.get('timestamp')
            try:
                # This handles strings, pd.Timestamp, and numpy datetime64
                ts_ms = int(pd.to_datetime(ts_val).timestamp() * 1000)
            except Exception:
                try:
                    ts_ms = int(ts_val)
                except (ValueError, TypeError):
                    ts_ms = 0
                
            val = row.get('load_p', row.get('load', 0))
            points.append(OHLCVPoint(
                timestamp=ts_ms,
                close=val,
                open=val,
                high=val,
                low=val
            ))

        print("\n⚠️  System entering TensorFlow training phase.")
        # 2. Standard LSTM
        if arch_type in ["all", "lstm_std"]:
            print("\n🚀 Step [1/1]: Initializing Standard LSTM Training...")
            report["steps"].append("Starting Standard LSTM training...")
            lstm_std_res = await lstm_forecaster.train_all(points, architecture="standard")
            report["architectures"]["lstm_standard"] = {
                "status": "success",
                "rmse": lstm_std_res.get("metrics", {}).get("rmse"),
                "mae": lstm_std_res.get("metrics", {}).get("mae")
            }
            print("✅ Standard LSTM Training Complete.")
            report["steps"].append("Standard LSTM training complete.")

        # 3. Bidirectional LSTM
        if arch_type in ["all", "lstm_bidi"]:
            print("\n🚀 Step [1/1]: Initializing Bidirectional LSTM Training...")
            report["steps"].append("Starting Bidirectional LSTM training...")
            lstm_bidi_res = await lstm_forecaster.train_all(points, architecture="bidirectional")
            report["architectures"]["lstm_bidirectional"] = {
                "status": "success",
                "rmse": lstm_bidi_res.get("metrics", {}).get("rmse"),
                "mae": lstm_bidi_res.get("metrics", {}).get("mae")
            }
            print("✅ Bidirectional LSTM Training Complete.")
            report["steps"].append("Bidirectional LSTM training complete.")
        report["steps"].append("All models saved to models/ directory.")

        # Generate a formatted text report
        lgbm = report['architectures'].get('lightgbm', {})
        std = report['architectures'].get('lstm_standard', {})
        bidi = report['architectures'].get('lstm_bidirectional', {})

        text_report = f"""ENERLYTICS NEXUS - AI AUDIT REPORT
==========================================
Date: {report['timestamp']}
Total Samples: {report['total_rows']}
Architecture Request: {arch_type.upper()}

ARCHITECTURES:
--------------
1. LIGHTGBM (Advanced):
   - RMSE: {lgbm.get('rmse', 'N/A')}
   - MAE:  {lgbm.get('mae', 'N/A')}

2. STANDARD LSTM:
   - RMSE: {std.get('rmse', 'N/A')}
   - MAE:  {std.get('mae', 'N/A')}

3. BIDIRECTIONAL LSTM:
   - RMSE: {bidi.get('rmse', 'N/A')}
   - MAE:  {bidi.get('mae', 'N/A')}

STEPS PERFORMED:
{"".join([' - ' + s + '\n' for s in report['steps']])}

CONCLUSION:
Serialization complete. Weights are now persisted in the Audit Engine for active forecasting.
"""
        return {"json": report, "text": text_report}

    except Exception as e:
        print(f"Training failed: {e}")
        return {"error": str(e)}

@router.post("/train/all")
async def train_all(request: Dict):
    return await _execute_training_pipeline(request.get("data"), "all")

@router.post("/train/lightgbm")
async def train_lightgbm(request: Dict):
    return await _execute_training_pipeline(request.get("data"), "lightgbm")

@router.post("/train/lstm_std")
async def train_lstm_std(request: Dict):
    return await _execute_training_pipeline(request.get("data"), "lstm_std")

@router.post("/train/lstm_bidi")
async def train_lstm_bidi(request: Dict):
    return await _execute_training_pipeline(request.get("data"), "lstm_bidi")
