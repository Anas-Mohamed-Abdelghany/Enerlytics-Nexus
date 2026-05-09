import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from .energy_tariff_service import get_tou_band, is_italian_holiday

def build_features(df: pd.DataFrame, is_training: bool = True) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Expert-level feature engineering for energy load forecasting.
    Includes cyclical time encoding, multi-scale lags, rolling stats, 
    and energy-specific domain features (TOU bands, solar elevation).
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # 1. Cyclical Encoding
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['dow'] = df['timestamp'].dt.dayofweek
    df['dow_sin'] = np.sin(2 * np.pi * df['dow'] / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df['dow'] / 7)
    
    df['month'] = df['timestamp'].dt.month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # 2. Lag Features (No look-ahead: shift load_kw by at least 1)
    # Lags: 15m (1), 1h (4), 24h (96), 48h (192), 1w (672)
    lags = [1, 4, 96, 192, 672]
    for lag in lags:
        df[f'load_lag_{lag}'] = df['load_kw'].shift(lag)
        df[f'solar_lag_{lag}'] = df['pv_kw'].shift(lag)

    # 3. Rolling & Oscillator Features (Technical Analysis)
    # 4-hour (16), 24-hour (96), 1-week (672)
    for window in [16, 96, 672]:
        # SMA & EMA
        df[f'load_sma_{window}'] = df['load_kw'].shift(1).rolling(window=window).mean()
        df[f'load_ema_{window}'] = df['load_kw'].shift(1).ewm(span=window, adjust=False).mean()
        df[f'load_std_{window}'] = df['load_kw'].shift(1).rolling(window=window).std()

    # Relative Strength Index (RSI) - Detects "Load Exhaustion"
    def compute_rsi(series, window=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    df['load_rsi'] = compute_rsi(df['load_kw'].shift(1), window=16) # 4-hour RSI
    
    # MACD-style Momentum (EMA 16 - EMA 96)
    df['load_momentum'] = df['load_ema_16'] - df['load_ema_96']

    # 4. Binary Flags
    df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6]).astype(int)
    df['is_holiday'] = df['timestamp'].apply(is_italian_holiday).astype(int)

    # 5. ToU Band (One-Hot Encoding)
    df['tou_band'] = df['timestamp'].apply(get_tou_band)
    for band in ['F1', 'F2', 'F3']:
        df[f'band_{band}'] = (df['tou_band'] == band).astype(int)

    # 6. Solar Elevation Proxy (lat=45.5 for Milan)
    # Simplified solar elevation calculation
    lat_rad = np.radians(45.5)
    # Day of year
    doy = df['timestamp'].dt.dayofyear
    # Declination
    declination = np.radians(23.45 * np.sin(np.radians(360 / 365 * (doy - 81))))
    # Hour angle (approximate: noon is 0, each hour is 15 deg)
    hour_angle = np.radians(15 * (df['hour'] - 12))
    # Sin of solar elevation
    df['solar_elevation_sin'] = np.sin(lat_rad) * np.sin(declination) + \
                                np.cos(lat_rad) * np.cos(declination) * np.cos(hour_angle)
    df['solar_elevation'] = np.arcsin(df['solar_elevation_sin'].clip(-1, 1))

    # 7. Clean up
    feature_cols = [
        'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'month_sin', 'month_cos',
        'is_weekend', 'is_holiday', 'band_F1', 'band_F2', 'band_F3', 'solar_elevation'
    ]
    feature_cols += [f'load_lag_{l}' for l in lags]
    feature_cols += [f'solar_lag_{l}' for l in lags]
    feature_cols += ['load_sma_16', 'load_sma_96', 'load_sma_672']
    feature_cols += ['load_ema_16', 'load_ema_96', 'load_ema_672']
    feature_cols += ['load_std_16', 'load_std_96', 'load_std_672']
    feature_cols += ['load_rsi', 'load_momentum']

    # Target
    y = df['load_kw']
    X = df[feature_cols]

    # Drop NaNs introduced by lags/rolling
    valid_idx = X.dropna().index
    X = X.loc[valid_idx]
    y = y.loc[valid_idx]

    return X, y, feature_cols
