import os
import asyncio
import joblib
import numpy as np
import pandas as pd
import pandas_ta as ta
import shap
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from lightgbm import LGBMRegressor, log_evaluation
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from astral import LocationInfo
from astral.sun import sun
import holidays

# Configuration
LATITUDE = 45.4
LONGITUDE = 9.2
CITY = "Milan"
REGION = "Italy"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])

class EnergyForecaster:
    def __init__(self):
        self.load_model = None
        self.solar_model = None
        self.load_q90 = 0.0
        self.solar_q90 = 0.0
        self.scaler = StandardScaler()
        self.feature_names = []
        self.ita_holidays = holidays.Italy(years=[2024, 2025])
        self.location = LocationInfo(CITY, REGION, "Europe/Rome", LATITUDE, LONGITUDE)
        
        # Auto-load existing models if present
        self._load_saved_assets()

    def _load_saved_assets(self):
        try:
            load_path = os.path.join(MODEL_DIR, 'lgbm_load.pkl')
            solar_path = os.path.join(MODEL_DIR, 'lgbm_solar.pkl')
            scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
            
            if os.path.exists(load_path):
                load_data = joblib.load(load_path)
                if isinstance(load_data, dict):
                    self.load_model = load_data.get('model')
                    self.load_q90 = load_data.get('q90', 0.0)
                else:
                    self.load_model = load_data
                print(f"✅ Loaded Energy Load Model from {load_path}")
                
            if os.path.exists(solar_path):
                solar_data = joblib.load(solar_path)
                if isinstance(solar_data, dict):
                    self.solar_model = solar_data.get('model')
                    self.solar_q90 = solar_data.get('q90', 0.0)
                else:
                    self.solar_model = solar_data
                    
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            # Load feature names
            feat_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
            if os.path.exists(feat_path):
                self.feature_names = joblib.load(feat_path)
                print(f"✅ Loaded Feature Schema: {len(self.feature_names)} features")
        except Exception as e:
            print(f"⚠️ Could not auto-load energy models: {e}")

    def build_energy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature Engineering for LOAD and SOLAR forecasting.
        """
        df = df.copy()
        # Clean column names
        df.columns = [c.strip() for c in df.columns]
        
        # Normalize column names for robust inference
        if 'Selling_price_eur_kwh' in df.columns:
            df = df.rename(columns={'Selling_price_eur_kwh': 'price'})
        elif 'selling_price' in df.columns:
            df = df.rename(columns={'selling_price': 'price'})
        elif 'close' in df.columns:
            df = df.rename(columns={'close': 'price'})
            
        if 'load_p' in df.columns:
            df = df.rename(columns={'load_p': 'load'})
        if 'pv_p' in df.columns:
            df = df.rename(columns={'pv_p': 'solar'})

        print(f"DEBUG: Shape: {df.shape}, Columns: {list(df.columns)}")
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors='coerce')
        
        # Drop rows where index could not be parsed
        df = df[df.index.notnull()]

        # 1. Time features (Sin/Cos + Fourier)
        df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        
        # Fourier Features for daily/weekly periodicity
        for k in range(1, 4):
            df[f'fourier_daily_sin_{k}'] = np.sin(2 * k * np.pi * df.index.hour / 24)
            df[f'fourier_daily_cos_{k}'] = np.cos(2 * k * np.pi * df.index.hour / 24)
            
        df['hour'] = df.index.hour
        df['dayofweek'] = df.index.dayofweek
        df['month'] = df.index.month
        
        # 1. Cyclical Time Encoding (Fourier Transforms)
        # Prevents model from thinking hour 23 and hour 0 are far apart
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)

        df['is_weekend'] = df.index.dayofweek >= 5
        df['is_holiday'] = df.index.map(lambda x: x in self.ita_holidays)

        # 2. Technical Indicators (Oscillators) using pandas_ta
        # LightGBM benefits greatly from these momentum indicators
        if 'price' in df.columns:
            # Momentum / Oscillators
            df['rsi_14'] = ta.rsi(df['price'], length=14)
            macd = ta.macd(df['price'])
            if macd is not None:
                df['macd'] = macd['MACD_12_26_9']
                df['macd_signal'] = macd['MACDs_12_26_9']
            
            # Volatility / Range
            df['price_range_24h'] = df['price'].rolling(96).max() - df['price'].rolling(96).min()
            df['price_volatility_24h'] = df['price'].rolling(96).std()
            
            # Trend
            df['ema_24h'] = ta.ema(df['price'], length=96) # 24h moving average
            df['price_roc_1h'] = ta.roc(df['price'], length=4) # 1h Rate of Change
            
            # Italian ToU (F1/F2/F3 Bands)
            # F1: Peak (Mon-Fri 08:00-19:00)
            # F2: Mid-Peak (Mon-Fri 07-08, 19-23; Sat 07-23)
            # F3: Off-Peak (Mon-Sat 23-07; Sun/Holidays All Day)
            hour = df.index.hour
            dow = df.index.dayofweek
            is_holiday = df['is_holiday']

            df['tariff_f1'] = (dow < 5) & (hour >= 8) & (hour < 19) & (~is_holiday)
            df['tariff_f2'] = (((dow < 5) & ((hour == 7) | ((hour >= 19) & (hour < 23)))) | \
                               ((dow == 5) & (hour >= 7) & (hour < 23))) & (~is_holiday)
            df['tariff_f3'] = (~df['tariff_f1']) & (~df['tariff_f2'])

            # ToU Patterns
            df['is_peak_hour'] = df['tariff_f1']

        # 3. Temperature Proxy (Seasonal + Daily estimation for Milan)
        # Based on Milan averages: Jan ~3°C, July ~25°C
        # Annual wave + daily wave
        day_of_year = df.index.dayofyear
        hour = df.index.hour
        # Annual cycle: peak in July (day 200)
        annual_temp = 14 + 11 * np.cos(2 * np.pi * (day_of_year - 200) / 365)
        # Daily cycle: peak at 15:00
        daily_variation = 4 * np.cos(2 * np.pi * (hour - 15) / 24)
        df['temp_estimate'] = annual_temp + daily_variation
        # Heating/Cooling Degree Days based strictly on Month (Milan Historical Averages)
        monthly_hdd = {1: 15, 2: 13, 3: 9, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 4, 11: 10, 12: 14}
        monthly_cdd = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 4, 7: 7, 8: 6, 9: 2, 10: 0, 11: 0, 12: 0}
        
        df['hdd'] = df['month'].map(monthly_hdd)
        df['cdd'] = df['month'].map(monthly_cdd)
        
        # Explicit Seasonal Regimes (Summer vs Winter behavior)
        df['is_summer'] = df['month'].isin([6, 7, 8, 9])
        df['is_winter'] = df['month'].isin([12, 1, 2, 3])
        df['is_shoulder'] = df['month'].isin([4, 5, 10, 11])

        def get_solar_features(dt):
            try:
                s = sun(self.location.observer, date=dt.date())
                sunrise = s['sunrise'].replace(tzinfo=None)
                sunset = s['sunset'].replace(tzinfo=None)
                naive_dt = dt.replace(tzinfo=None)
                
                since_sunrise = (naive_dt - sunrise).total_seconds() / 3600
                until_sunset = (sunset - naive_dt).total_seconds() / 3600
                return pd.Series([since_sunrise, until_sunset])
            except Exception:
                return pd.Series([0.0, 0.0])

        solar_data = df.index.to_series().apply(get_solar_features)
        df['time_since_sunrise_h'] = solar_data[0].values
        df['time_until_sunset_h'] = solar_data[1].values
        
        # Explicit Day/Night binary feature based on solar position
        df['is_daytime'] = (df['time_since_sunrise_h'] > 0) & (df['time_until_sunset_h'] > 0)



        # 4. Behavioral & Economic Features (Advanced)
        if 'load' in df.columns and 'solar' in df.columns:
            # SHIFT BY 1 to prevent data leakage (we don't know current load/solar when predicting)
            shifted_load = df['load'].shift(1)
            shifted_solar = df['solar'].shift(1)
            
            df['net_load'] = shifted_load - shifted_solar
            df['net_load_rolling_mean_4h'] = df['net_load'].rolling(16).mean()
        
        # Cumulative energy used today (resets at midnight)
        if 'load' in df.columns:
            shifted_load = df['load'].shift(1)
            df['daily_cumulative_load'] = shifted_load.groupby(df.index.date).cumsum()
            
            # Exponential Moving Averages (EMA) - Weights recent hours higher
            df['load_ema_3h'] = shifted_load.ewm(span=12).mean() # 12 * 15m = 3h
            df['load_ema_12h'] = shifted_load.ewm(span=48).mean()
            
            # Change compared to exactly 24 hours ago
            df['load_trend_24h'] = shifted_load - df['load'].shift(96)
            # Sudden spikes (Volatility)
            df['load_volatility_1h'] = shifted_load.rolling(4).std()

        if 'price' in df.columns:
            # Price context (Is it expensive relative to the day?)
            price_mean_24h = df['price'].rolling(96, min_periods=1).mean()
            df['price_relative_to_24h'] = df['price'] / price_mean_24h
            # Price trend
            df['price_diff_1h'] = df['price'].diff(4)

        # 5. Lag and Aggregation features for LOAD
        if 'load' in df.columns:
            for lag in [96, 192, 672]: # 1d, 2d, 1w
                df[f'load_lag_{lag}'] = df['load'].shift(lag)
            df['load_rolling_mean_96'] = df['load'].shift(1).rolling(96).mean()
            df['load_rolling_max_24h'] = df['load'].shift(1).rolling(96).max()

        # 6. Lag features for SOLAR
        if 'solar' in df.columns:
            for lag in [96, 672]:
                df[f'solar_lag_{lag}'] = df['solar'].shift(lag)
            df['solar_rolling_mean_96'] = df['solar'].shift(1).rolling(96).mean()

        # NaN handling (ffill + bfill)
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        
        # Replace infinities caused by division by zero (e.g. price mean = 0)
        df.replace([np.inf, -np.inf], 0, inplace=True)
        
        # Drop columns that are entirely NaN (e.g. metadata columns from previous exports)
        df = df.dropna(axis=1, how='all')
        
        nan_counts = df.isna().sum()
        if nan_counts.any():
            print(f"DEBUG: NaNs found before dropna:\n{nan_counts[nan_counts > 0]}")
            
        final_df = df.dropna()
        print(f"DEBUG: Feature Engineering - Original rows: {len(df)}, Valid rows after lags: {len(final_df)}")
        return final_df

    async def train_pipeline(self, data: pd.DataFrame):
        """
        Asynchronous training pipeline.
        """
        # Set the correct index before processing
        if 'timestamp' in data.columns:
            # Frontend sends timestamps in milliseconds (epoch)
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms', errors='coerce')
            data = data.set_index('timestamp')
        else:
            # Fallback: try to convert existing index if it looks like strings
            data.index = pd.to_datetime(data.index, errors='coerce')
            
        data = data[data.index.notnull()]
        data = data[~data.index.duplicated(keep='first')]
        data = data.sort_index()
        
        # Normalize column names for the forecaster
        # Priority: Selling_price_eur_kwh > selling_price > close
        if 'Selling_price_eur_kwh' in data.columns:
            data = data.rename(columns={'Selling_price_eur_kwh': 'price'})
        elif 'selling_price' in data.columns:
            data = data.rename(columns={'selling_price': 'price'})
        elif 'close' in data.columns:
            data = data.rename(columns={'close': 'price'})
            
        if 'load_p' in data.columns:
            data = data.rename(columns={'load_p': 'load'})
        if 'pv_p' in data.columns:
            data = data.rename(columns={'pv_p': 'solar'})

        # Ensure we have at least one target
        if 'load' not in data.columns and 'solar' not in data.columns:
            raise ValueError("Dataset must contain 'load' or 'load_p' columns.")

        # Build energy features on the ENTIRE dataset first
        # This ensures validation set has its history for lags
        full_feat = self.build_energy_features(data)
        
        if len(full_feat) < 200:
            raise ValueError(f"Insufficient data after feature engineering. Need more than 1 week of data. Found {len(full_feat)} rows.")

        # Dynamic Split on the FEATURE dataframe
        split_idx = int(len(full_feat) * 0.8)
        train_feat = full_feat.iloc[:split_idx].copy()
        val_feat = full_feat.iloc[split_idx:].copy()

        targets = [t for t in ['load', 'solar'] if t in train_feat.columns]
        if not targets:
            raise ValueError("No valid target columns (load/solar) found after feature engineering.")
            
        excluded = ['load', 'solar', 'price', 'close', 'integrity_flags', 'is_forecast', 'timestamp']
        features = [c for c in train_feat.columns if c not in excluded]
        self.feature_names = features

        X_train = pd.DataFrame(self.scaler.fit_transform(train_feat[features].astype(float)), columns=features)
        X_val = pd.DataFrame(self.scaler.transform(val_feat[features].astype(float)), columns=features)

        results = {}

        for target in targets:
            y_train = np.maximum(train_feat[target].values, 0)
            y_val = np.maximum(val_feat[target].values, 0)

            lgbm = LGBMRegressor(
                n_estimators=1000,
                learning_rate=0.04,
                num_leaves=31,  # Reduced from 63 to prevent overfitting on the new complex features
                min_child_samples=20,
                objective='tweedie',
                tweedie_variance_power=1.5, # 1.5 is perfect for right-skewed energy load data
                colsample_bytree=0.8,       # Feature fraction to prevent overfitting
                random_state=42
            )
            
            lgbm.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
            )

            # Manual Conformal Prediction (Residual-based)
            y_pred_val = lgbm.predict(X_val)
            residuals = np.abs(y_val - y_pred_val)
            # Store the 90th percentile residual for 90% confidence intervals
            q_90 = np.percentile(residuals, 90)
            
            mae = mean_absolute_error(y_val, y_pred_val)
            rmse = root_mean_squared_error(y_val, y_pred_val)
            results[f'{target}_mae'] = float(mae)
            results[f'{target}_rmse'] = float(rmse)

            # Store model and quantile
            if target == 'load':
                self.load_model = lgbm
                self.load_q90 = float(q_90)
                joblib.dump({'model': lgbm, 'q90': q_90}, os.path.join(MODEL_DIR, 'lgbm_load.pkl'))
            else:
                self.solar_model = lgbm
                self.solar_q90 = float(q_90)
                joblib.dump({'model': lgbm, 'q90': q_90}, os.path.join(MODEL_DIR, 'lgbm_solar.pkl'))

        joblib.dump(self.scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
        joblib.dump(self.feature_names, os.path.join(MODEL_DIR, 'feature_names.pkl'))
        return results

# Singleton instance
forecaster = EnergyForecaster()

@router.post("/train")
async def train_forecast(background_tasks: BackgroundTasks, data: List[Dict]):
    try:
        df = pd.DataFrame(data)
        if df.empty:
            raise HTTPException(status_code=400, detail="Empty data provided")
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, lambda: asyncio.run(forecaster.train_pipeline(df)))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict_forecast(req: Dict):
    try:
        hours_ahead = req.get('hours_ahead', 24)
        current_ts = pd.to_datetime(req.get('current_timestamp', datetime.now()))
        weather = req.get('weather_forecast', {})

        future_ts = [current_ts + timedelta(minutes=15 * i) for i in range(hours_ahead * 4)]
        df_future = pd.DataFrame(index=future_ts)
        
        df_future['temperature_2m'] = weather.get('temperature_2m', [20] * len(future_ts))
        df_future['cloud_cover'] = weather.get('cloud_cover', [0] * len(future_ts))
        df_future['direct_radiation'] = weather.get('direct_radiation', [0] * len(future_ts))
        df_future['relative_humidity'] = weather.get('relative_humidity', [50] * len(future_ts))

        # We need historical data to compute 24h+ lags!
        hist_data = req.get('historical_data', [])
        df_hist = pd.DataFrame(hist_data)
        
        if not df_hist.empty:
            df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
            df_hist.set_index('timestamp', inplace=True)
            
            # Align columns if necessary, then concatenate
            df_combined = pd.concat([df_hist, df_future])
            feat_df_combined = forecaster.build_energy_features(df_combined)
            
            # Slice only the future rows for prediction
            feat_df = feat_df_combined.loc[df_future.index]
        else:
            # Fallback (will result in NaNs for lags, but avoids structural crash)
            feat_df = forecaster.build_energy_features(df_future)
        X = pd.DataFrame(
            forecaster.scaler.transform(feat_df[forecaster.feature_names]),
            columns=forecaster.feature_names
        )

        res = {}
        for name, model, q90 in [('load', forecaster.load_model, forecaster.load_q90), 
                                ('solar', forecaster.solar_model, forecaster.solar_q90)]:
            if model:
                y_pred = model.predict(X)
                res[f'{name}_forecast'] = y_pred.tolist()
                # Manual intervals using the stored 90th percentile residual
                res[f'{name}_lower'] = (y_pred - q90).tolist()
                res[f'{name}_upper'] = (y_pred + q90).tolist()
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shap")
async def get_shap_explainer():
    try:
        if not forecaster.load_model:
            raise HTTPException(status_code=404, detail="Model not trained")
        
        lgbm = forecaster.load_model
        explainer = shap.TreeExplainer(lgbm)
        
        X_sample = np.random.randn(100, len(forecaster.feature_names))
        shap_values = explainer.shap_values(X_sample)
        
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        importance = {name: float(val) for name, val in zip(forecaster.feature_names, mean_abs_shap)}
        sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])

        instance_shap = shap_values[0]
        waterfall = {
            "features": forecaster.feature_names,
            "shap_values": instance_shap.tolist(),
            "base_value": float(explainer.expected_value)
        }

        return {
            "top_10_importance": sorted_importance,
            "waterfall": waterfall
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
