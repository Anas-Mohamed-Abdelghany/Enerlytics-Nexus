from fastapi import APIRouter, HTTPException
from models.schemas import BatteryOptimizationRequest, BatteryOptimizationResponse, OHLCVPoint
from core.services.battery_optimizer import optimize_battery, compute_baseline_cost
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
        # Cleanup inputs: ensure no NaNs or Infs reach the optimizer
        buy_price = np.nan_to_num(np.array(request.price_forecast), nan=0.25)
        sell_price = np.nan_to_num(np.array(request.sell_price_forecast), nan=0.20) if request.sell_price_forecast else buy_price * 0.8
        load_forecast = np.nan_to_num(np.array(request.load_forecast), nan=1.5)
        solar_forecast = np.nan_to_num(np.array(request.solar_forecast), nan=0.0)

        result = optimize_battery(
            buy_price=buy_price,
            sell_price=sell_price,
            load_forecast=load_forecast,
            solar_forecast=solar_forecast,
            soc_init=request.soc_init,
            battery_capacity_kwh=request.battery_capacity_kwh or 16.0,
            p_max_kw=request.p_max_kw or 8.0,
            grid_limit_kw=request.grid_limit_kw or 6.0
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=f"Optimization failed: {result.get('message', 'Unknown error')}")

        # Calculate baseline (Grid-Only) cost for comparison
        baseline_cost = compute_baseline_cost(buy_price, sell_price, load_forecast, solar_forecast)
        
        # Format results for the frontend Response Schema
        total_cost = np.sum(result["cost_eur"])
        savings_eur = baseline_cost - total_cost
        savings_pct = (savings_eur / baseline_cost * 100) if baseline_cost > 0 else 0

        # Add synthetic timestamps for the 15-min intervals
        start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        formatted_result = {
            "status": "success" if result["success"] else "failed",
            "soc_trajectory": result["soc"].tolist(),
            "charge_schedule": result["p_charge_kw"].tolist(),
            "discharge_schedule": result["p_discharge_kw"].tolist(),
            "grid_import": result["p_grid_import_kw"].tolist(),
            "grid_export": result["p_grid_export_kw"].tolist(),
            "total_cost_eur": float(total_cost),
            "baseline_cost_eur": float(baseline_cost),
            "savings_eur": float(savings_eur),
            "savings_pct": float(savings_pct),
            "timestamps": [start_time + timedelta(minutes=15*i) for i in range(len(request.price_forecast))]
        }
        
        return formatted_result
    except Exception as e:
        import traceback
        print(f"ERROR: Optimization route failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate", response_model=BatteryOptimizationResponse)
async def run_rolling_mpc_simulation(request: BatteryOptimizationRequest):
    """
    Simulate a long-term rolling horizon MPC (O(N*LP_solve)).
    """
    try:
        from core.services.battery_optimizer import rolling_mpc_optimize
        buy_price = np.array(request.price_forecast)
        sell_price = np.array(request.sell_price_forecast) if request.sell_price_forecast else buy_price * 0.8
        
        result = rolling_mpc_optimize(
            buy_price=buy_price,
            sell_price=sell_price,
            load_forecast=np.array(request.load_forecast),
            solar_forecast=np.array(request.solar_forecast),
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

def get_tou_price(ts):
    """Returns the Italian ToU price for a given timestamp."""
    # Safety: ensure we have a datetime object
    if isinstance(ts, str):
        ts = pd.to_datetime(ts)
        
    hour = ts.hour
    weekday = ts.weekday() # 0=Mon, 5=Sat, 6=Sun
    date = ts.date()

    if weekday < 5: # Mon-Fri
        if 8 <= hour < 19:
            return 0.2540 # F1
        elif (7 <= hour < 8) or (19 <= hour < 23):
            return 0.2682 # F2
        else:
            return 0.2440 # F3
    elif weekday == 5: # Sat
        if 7 <= hour < 23:
            return 0.2682 # F2
        else:
            return 0.2440 # F3
    else: # Sun
        return 0.2440 # F3

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

    # 1. Determine the audit window based on the requested horizon
    # Translate sidebar labels (1M, 3M, 1W) to day counts
    horizon_val = str(request.get("horizon", "audit"))
    horizon_map = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "30": 30, "Month 3 Audit": 31}
    
    days_horizon = None
    if horizon_val in horizon_map:
        days_horizon = horizon_map[horizon_val]
    elif horizon_val.isdigit():
        days_horizon = int(horizon_val)

    if horizon_val == "Month 3 Audit":
        # Strict filter for March only
        df_to_audit = df[df['timestamp'].dt.month == 3].copy()
        if not df_to_audit.empty:
            max_ts = df_to_audit['timestamp'].max()
            found_periods = [(3, max_ts.year, "March Audit Window")]
            df = df_to_audit
            days_horizon = 31
        else:
            days_horizon = None # Fallback if no March data
    elif days_horizon:
        # Filter for the last N days
        max_ts = df['timestamp'].max()
        start_ts = max_ts - pd.Timedelta(days=days_horizon)
        df_to_audit = df[df['timestamp'] > start_ts].copy()
        
        # We'll treat this as one "Custom Window" for the UI
        month_name = f"Last {days_horizon} Days"
        found_periods = [(0, max_ts.year, month_name)]
        # Replace the full df with our sliced version for the loop
        df = df_to_audit 
    else:
        # Detect all months present in the data
        months_in_data = df['timestamp'].dt.month.unique()
        years_in_data = df['timestamp'].dt.year.unique()
        month_map = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
                     7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        
        found_periods = []
        for yr in sorted(years_in_data):
            m_list = sorted(df[df['timestamp'].dt.year == yr]['timestamp'].dt.month.unique())
            for m in m_list:
                found_periods.append((m, yr, month_map[m]))
        
        # LOGIC FIX: If specifically requesting the hackathon "Audit", 
        # filter strictly for months 4 and 9 of the target year.
        if horizon_val.lower() == "audit":
            # Filter for months 4 and 9 in any year present, or ideally the target_year
            audit_periods = [p for p in found_periods if p[0] in [4, 9]]
            if audit_periods:
                found_periods = audit_periods
            else:
                # If 4/9 not found, keep the first 2 as fallback but print warning
                print(f"⚠️ Warning: Audit requested for months 4 & 9 but they were not found in the dataset. Available: {months_in_data}")
                found_periods = found_periods[:2]
        else:
            # Default: Limit to top 2 for UI to avoid overloading
            found_periods = found_periods[:2]

    results = {}
    overall_errors = []
    overall_actuals = []

    for month_num, target_year, month_name in found_periods:
        # Filter for the specific period
        if days_horizon:
            month_df = df.copy() # Already sliced
        else:
            month_df = df[(df['timestamp'].dt.year == target_year) & (df['timestamp'].dt.month == month_num)].copy()
        
        display_period = f"{month_name} {target_year}" if not days_horizon else month_name
        result_key = month_name.lower().replace(" ", "_")

        # Determine model file and scaler based on architecture
        current_arch = architecture
        if architecture == 'hybrid':
            # Dynamic Hybrid: Logic still exists but we can simplify if needed
            current_arch = 'advanced' 

        model_file = 'lgbm_load.pkl'
        scaler_file = 'scaler.pkl'
        
        if current_arch == 'standard': model_file = 'lstm_load_standard.h5'
        elif current_arch == 'bidirectional': model_file = 'lstm_load_bidi.h5'
        elif current_arch == 'advanced':
            # Dynamic Discovery
            m_lower = month_name.lower().split()[0] # e.g. "march"
            m_model = f'lgbm_load_{m_lower}.pkl'
            m_scaler = f'scaler_{m_lower}.pkl'
            
            if os.path.exists(os.path.join(MODEL_DIR, m_model)):
                model_file = m_model
                if os.path.exists(os.path.join(MODEL_DIR, m_scaler)):
                    scaler_file = m_scaler
            
            # Load the discovered model into the forecaster instance
            if model_file.endswith('.pkl') and os.path.exists(os.path.join(MODEL_DIR, model_file)):
                forecaster.load_model = joblib.load(os.path.join(MODEL_DIR, model_file))['model']
                if os.path.exists(os.path.join(MODEL_DIR, scaler_file)):
                    forecaster.scaler = joblib.load(os.path.join(MODEL_DIR, scaler_file))

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
                # IMPORTANT: Build features on the FULL dataset first to preserve history for lags/indicators
                # Then slice into the specific month
                full_feat_df = forecaster.build_energy_features(df.set_index('timestamp'))
                
                # Check for target year/month in the featured dataframe
                month_with_features = full_feat_df[(full_feat_df.index.year == target_year) & (full_feat_df.index.month == month_num)].copy()
                
                if month_with_features.empty:
                    # If empty, it might be because the year/month filtering failed or data is missing
                    # Fallback to engineering just the month_df as a last resort
                    print(f"⚠️ Warning: Full features slice for {month_name} {target_year} is empty. Falling back to month-only engineering.")
                    month_with_features = forecaster.build_energy_features(month_df.set_index('timestamp'))

                # 5. Price Vectors
                # 5. Price Vectors
                dt_timestamps = pd.to_datetime(month_with_features.index)
                buying_prices = np.array([get_tou_price(t) for t in dt_timestamps])
                selling_prices = month_with_features['price'].values if 'price' in month_with_features.columns else np.full(len(month_with_features), 0.10)
                
                # Extract solar and tariff bands from the featured df
                solars = month_with_features['solar'].values if 'solar' in month_with_features.columns else (month_with_features['pv_p'].values if 'pv_p' in month_with_features.columns else np.zeros(len(month_with_features)))
                t_f1 = month_with_features['tariff_f1'].values if 'tariff_f1' in month_with_features.columns else np.zeros(len(month_with_features), dtype=bool)
                t_f2 = month_with_features['tariff_f2'].values if 'tariff_f2' in month_with_features.columns else np.zeros(len(month_with_features), dtype=bool)
                t_f3 = month_with_features['tariff_f3'].values if 'tariff_f3' in month_with_features.columns else np.zeros(len(month_with_features), dtype=bool)

                if current_arch in ["advanced", "lightgbm"] and forecaster.load_model:
                    # LightGBM Path
                    # 1. Determine which feature schema to use
                    special_feat_path = os.path.join(MODEL_DIR, f'feature_names_{month_name.lower()}.pkl')
                    feat_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
                    
                    schema_features = []
                    if os.path.exists(special_feat_path):
                        schema_features = joblib.load(special_feat_path)
                    elif hasattr(forecaster.scaler, 'feature_names_in_'):
                        # Best source of truth: the scaler itself knows what it was fitted with
                        schema_features = list(forecaster.scaler.feature_names_in_)
                    elif os.path.exists(feat_path):
                        schema_features = joblib.load(feat_path)
                    else:
                        schema_features = forecaster.feature_names

                    # Update the forecaster instance so it's consistent
                    forecaster.feature_names = schema_features
                    
                    # 2. DEFENSIVE: Match the dataframe features exactly to what the Scaler knows
                    # This prevents the "Feature names unseen at fit time" error
                    known_features = getattr(forecaster.scaler, 'feature_names_in_', schema_features)
                    
                    for feat in known_features:
                        if feat not in month_with_features.columns:
                            month_with_features[feat] = 0.0

                    # 3. Select only the known features and scale
                    X_data = month_with_features[known_features].astype(float)
                    X_scaled = forecaster.scaler.transform(X_data)
                    X = pd.DataFrame(X_scaled, columns=known_features)
                    
                    # Ensure the model also receives what it expects
                    # (Usually model and scaler feature sets are identical)
                    predictions = forecaster.load_model.predict(X)
                    actuals = month_with_features['load'].values if 'load' in month_with_features.columns else month_with_features['load_p'].values
                    timestamps = month_with_features.index.strftime('%Y-%m-%dT%H:%M:%S').tolist()
                elif architecture in ["standard", "bidirectional"]:
                    # LSTM Path
                    from core.services.lstm_forecaster import predict_lstm_batch
                    predictions = predict_lstm_batch(month_df, architecture=architecture)
                    actuals = month_df['load_p'].values
                    timestamps = month_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist()
                    
                    # LSTM consumes the first 'lookback' (60) rows to make the first prediction
                    # Align all arrays to the end
                    if len(actuals) > len(predictions):
                        offset = len(actuals) - len(predictions)
                        actuals = actuals[offset:]
                        timestamps = timestamps[offset:]
                        solars = solars[offset:] if len(solars) >= len(actuals) else np.zeros(len(predictions))
                        buying_prices = buying_prices[offset:] if len(buying_prices) >= len(actuals) else np.zeros(len(predictions))
                    elif len(predictions) > len(actuals):
                        predictions = predictions[-len(actuals):]
                else:
                    raise ValueError(f"Unsupported architecture: {architecture}")

            except Exception as e:
                print(f"Prediction failed for {month_name} ({architecture}): {e}")
                import traceback
                traceback.print_exc()
                return {"error": f"Audit Failed: {str(e)}. Please ensure your model is trained for {architecture}."}
        else:
            # NO FAKE DATA - Raise error if model missing
            return {"error": f"Model file for '{arch_label}' not found. You must train the model first using the AI Strategy panel or the training script."}

        predictions = np.maximum(0.1, predictions)
        
        # ENFORCE OFFICIAL Italian ToU Prices for Audit Accuracy
        buying_prices = np.array([get_tou_price(t) for t in timestamps])
        
        # Defensive check against NaNs in raw dataset (causes sklearn metric crash)
        valid_idx = ~np.isnan(actuals) & ~np.isnan(predictions)
        if not np.all(valid_idx):
            actuals = actuals[valid_idx]
            predictions = predictions[valid_idx]
            timestamps = np.array(timestamps)[valid_idx].tolist()
            solars = solars[valid_idx]
            buying_prices = buying_prices[valid_idx]
            
        if len(actuals) == 0:
            return {"error": f"Audit Failed: No valid data points remaining for {month_name}."}

        metrics = compute_metrics(actuals, predictions)
        
        # Initialize the month results first to avoid KeyError
        results[month_name.lower()] = {
            "period": display_period,
            "source": prediction_source,
            "nrmse": round(metrics['nrmse'], 2),
            "rmse": round(metrics['rmse'], 3),
            "mae": round(metrics['mae'], 3),
            "points": len(actuals),
            "series": []
        }

        # RUN BATTERY OPTIMIZATION for the Audit Month
        try:
            from core.services.battery_optimizer import rolling_mpc_optimize
            # Note: We use the PREDICTIONS (load_new) for the controller to stay realistic
            # but calculate costs using ACTUAL prices if available. 
            # In the Solship hackathon, we use predicted loads for dispatch decisions.
            
            opt_result = rolling_mpc_optimize(
                buy_price=buying_prices,
                sell_price=buying_prices * 0.8, # Default export price logic
                load_forecast=predictions,      # Decisions based on predicted load
                solar_forecast=solars,
                soc_init=0.5,
                battery_capacity_kwh=16.0,
                p_max_kw=8.0,
                grid_limit_kw=6.0
            )
            
            # Re-calculate costs using ACTUAL loads for the "True" bill
            # Cost = (NetGrid * Price) * dt
            # NetGrid = Load - Solar - BatteryP
            # BatteryP = Charge + Discharge
            
            # Correct logic: Charging increases net grid flow (import), Discharging decreases it.
            # opt_actions (Battery Output) = Discharge - Charge
            p_charge = np.array(opt_result["charge_schedule"])
            p_discharge = np.array(opt_result["discharge_schedule"])
            opt_actions = p_discharge - p_charge
            net_grid_opt = actuals - solars - opt_actions
            
            # Baseline (Battery = 0)
            net_grid_base = actuals - solars
            
            # bill calculation (15 min = 0.25h)
            dt = 0.25
            
            def calc_bill(net_grid, prices):
                p_imp = np.maximum(0, net_grid)
                p_exp = np.maximum(0, -net_grid)
                return np.sum(p_imp * prices - p_exp * (prices * 0.8)) * dt

            optimized_bill = calc_bill(net_grid_opt, buying_prices)
            baseline_bill = calc_bill(net_grid_base, buying_prices)
            savings = baseline_bill - optimized_bill

            # Self-Consumption Index (SCI) Math
            # Baseline SC: Min(Solar, Load) - what we use naturally
            # Optimized SC: Min(Solar + Discharge - Charge, Load) - what we use with battery
            # Note: discharge is positive, charge is negative. 
            # Energy used from solar = Load - GridImport (clamped to Solar)
            
            def calc_sc(net_grid, load_vals):
                import_vals = np.maximum(0, net_grid)
                return np.sum(load_vals - import_vals) # Energy NOT bought = energy used from solar/battery

            sc_base = calc_sc(net_grid_base, actuals)
            sc_opt = calc_sc(net_grid_opt, actuals)
            total_solar = np.sum(solars)
            
            sc_gain_pct = ((sc_opt - sc_base) / total_solar * 100) if total_solar > 0 else 0

            results[month_name.lower()]["optimization"] = {
                "optimized_bill": round(optimized_bill, 2),
                "baseline_bill": round(baseline_bill, 2),
                "savings": round(savings, 2),
                "savings_pct": round((savings / baseline_bill * 100), 2) if baseline_bill > 0 else 0,
                "sc_gain_pct": round(sc_gain_pct, 2),
                "schedule": [
                    {
                        "ts": timestamps[i],
                        "action_p_bat": round(float(opt_actions[i]), 3),
                        "soc": round(float(opt_result["soc_trajectory"][i]), 3),
                        "cost_eur": round(float((np.maximum(0, net_grid_opt[i]) * buying_prices[i] - np.maximum(0, -net_grid_opt[i]) * (buying_prices[i] * 0.8)) * dt), 4)
                    } for i in range(len(actuals))
                ]
            }
        except Exception as opt_err:
            print(f"Audit Optimization failed for {month_name}: {opt_err}")
            results[month_name.lower()]["optimization"] = {"error": str(opt_err)}

        overall_errors.extend(np.abs(actuals - predictions).tolist())
        overall_actuals.extend(actuals.tolist())

        results[month_name.lower()].update({
            "series": [
                {
                    "ts": timestamps[i],
                    "load_p": round(float(actuals[i]), 3),
                    "load_new": round(float(predictions[i]), 3),
                    "pv_p": round(float(solars[i]), 3),
                    "selling_price_eur_kwh": round(float(buying_prices[i]), 4),
                    "delta": round(float(predictions[i] - actuals[i]), 3),
                    "error_pct": round(abs(predictions[i] - actuals[i]) / actuals[i] * 100, 2) if actuals[i] > 0 else 0
                } for i in range(len(actuals))
            ]
        })

    # Calculate overall metrics
    if overall_actuals:
        mean_actual = np.mean(overall_actuals)
        mae = np.mean(overall_errors)
        rmse = np.sqrt(np.mean(np.array(overall_errors)**2))
        overall_nrmse = round((rmse / mean_actual * 100), 2) if mean_actual > 0 else 0
        overall_mae = round(mae, 3)
        overall_rmse = round(rmse, 3)
    else:
        overall_nrmse = 0
        overall_mae = 0
        overall_rmse = 0

    results["overall_nrmse"] = overall_nrmse
    results["overall_mae"] = overall_mae
    results["overall_rmse"] = overall_rmse
    print(f"📊 Final Audit Result - NRMSE: {overall_nrmse}%, MAE: {overall_mae}, RMSE: {overall_rmse}")
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
