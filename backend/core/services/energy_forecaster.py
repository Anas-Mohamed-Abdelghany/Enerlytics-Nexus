import os
import asyncio
import joblib
import numpy as np
import pandas as pd
import shap
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from lightgbm import LGBMRegressor
from mapie.regression import MapieRegressor
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
        self.scaler = StandardScaler()
        self.feature_names = []
        self.ita_holidays = holidays.Italy(years=[2024, 2025])
        self.location = LocationInfo(CITY, REGION, "Europe/Rome", LATITUDE, LONGITUDE)

    def build_energy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature Engineering for LOAD and SOLAR forecasting.
        """
        df = df.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # 1. Time features (Sin/Cos encoding)
        df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)
        df['is_weekend'] = df.index.dayofweek >= 5
        df['is_holiday'] = df.index.map(lambda x: x in self.ita_holidays)

        # 2. Solar Position (Astral)
        def get_solar_features(dt):
            s = sun(self.location.observer, date=dt.date())
            sunrise = s['sunrise'].replace(tzinfo=None)
            sunset = s['sunset'].replace(tzinfo=None)
            naive_dt = dt.replace(tzinfo=None)
            
            since_sunrise = (naive_dt - sunrise).total_seconds() / 3600
            until_sunset = (sunset - naive_dt).total_seconds() / 3600
            return pd.Series([since_sunrise, until_sunset])

        df[['time_since_sunrise_h', 'time_until_sunset_h']] = df.index.to_series().apply(get_solar_features)

        # 3. Lag features for LOAD
        if 'load' in df.columns:
            for lag in [96, 192, 672]:
                df[f'load_lag_{lag}'] = df['load'].shift(lag)
            df['load_rolling_mean_96'] = df['load'].shift(1).rolling(96).mean()
            df['load_rolling_std_96'] = df['load'].shift(1).rolling(96).std()

        # 4. Lag features for SOLAR
        if 'solar' in df.columns:
            for lag in [96, 192, 672]:
                df[f'solar_lag_{lag}'] = df['solar'].shift(lag)
            df['solar_rolling_mean_96'] = df['solar'].shift(1).rolling(96).mean()
            df['solar_rolling_std_96'] = df['solar'].shift(1).rolling(96).std()

        # 5. Price features
        if 'price' in df.columns:
            df['price_lag_96'] = df['price'].shift(96)
            df['price_rolling_mean_24h'] = df['price'].shift(1).rolling(96).mean()
            # Italian ToU (Peak: 08:00-20:00 Mon-Fri)
            df['is_peak_hour'] = (df.index.hour >= 8) & (df.index.hour < 20) & (df.index.dayofweek < 5)

        # NaN handling (ffill only)
        df.ffill(inplace=True)
        return df.dropna()

    async def train_pipeline(self, data: pd.DataFrame):
        """
        Asynchronous training pipeline.
        """
        data.index = pd.to_datetime(data.index)
        train_df = data[(data.index >= '2024-01-01') & (data.index <= '2024-10-31')].copy()
        val_df = data[(data.index >= '2024-11-01') & (data.index <= '2024-12-31')].copy()

        if train_df.empty or val_df.empty:
            raise ValueError("Insufficient data for 2024 train/val split.")

        train_feat = self.build_energy_features(train_df)
        val_feat = self.build_energy_features(val_df)

        targets = ['load', 'solar']
        features = [c for c in train_feat.columns if c not in targets]
        self.feature_names = features

        X_train = self.scaler.fit_transform(train_feat[features])
        X_val = self.scaler.transform(val_feat[features])

        results = {}

        for target in targets:
            y_train = train_feat[target]
            y_val = val_feat[target]

            lgbm = LGBMRegressor(
                n_estimators=1000,
                learning_rate=0.05,
                num_leaves=63,
                min_child_samples=20,
                random_state=42
            )
            
            lgbm.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                eval_metric='mae'
            )

            mapie = MapieRegressor(estimator=lgbm, method="plus", cv="prefit")
            mapie.fit(X_val, y_val)

            y_pred = mapie.predict(X_val)
            mae = mean_absolute_error(y_val, y_pred)
            rmse = root_mean_squared_error(y_val, y_pred)
            results[f'{target}_mae'] = float(mae)
            results[f'{target}_rmse'] = float(rmse)

            if target == 'load':
                self.load_model = mapie
                joblib.dump(mapie, os.path.join(MODEL_DIR, 'mapie_load.pkl'))
            else:
                self.solar_model = mapie
                joblib.dump(mapie, os.path.join(MODEL_DIR, 'mapie_solar.pkl'))

        joblib.dump(self.scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
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

        feat_df = forecaster.build_energy_features(df_future)
        X = forecaster.scaler.transform(feat_df[forecaster.feature_names])

        res = {}
        for name, model in [('load', forecaster.load_model), ('solar', forecaster.solar_model)]:
            if model:
                y_pred, y_cis = model.predict(X, alpha=0.1)
                res[f'{name}_forecast'] = y_pred.tolist()
                res[f'{name}_lower'] = y_cis[:, 0, 0].tolist()
                res[f'{name}_upper'] = y_cis[:, 1, 0].tolist()
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shap")
async def get_shap_explainer():
    try:
        if not forecaster.load_model:
            raise HTTPException(status_code=404, detail="Model not trained")
        
        lgbm = forecaster.load_model.estimator
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
