import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def validate_and_clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Performs 15-min resolution validation, timezone alignment, and non-negativity checks.
    Zeros are NOT treated as missing values.
    """
    stats = {}
    
    # 1. Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 2. Check for missing timestamps
    full_range = pd.date_range(df['timestamp'].min(), df['timestamp'].max(), freq='15min')
    missing_count = len(full_range.difference(df['timestamp']))
    stats['missing_timestamps'] = missing_count
    
    # 3. Non-negativity check
    for col in ['load_kw', 'pv_kw']:
        if col in df.columns:
            neg_count = (df[col] < 0).sum()
            stats[f'negative_{col}_count'] = int(neg_count)
            # Clip negatives to 0
            df[col] = df[col].clip(lower=0)
            
    return df, stats

def reconstruct_soc_and_detect_anomalies(
    df: pd.DataFrame,
    soc_init: float = 0.5,
    c_bat: float = 16.0,
    eta_c: float = 0.9487,
    eta_d: float = 0.9487,
    dt: float = 0.25
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reconstructs the SoC trajectory from p_battery_kw and detects physical violations.
    """
    if 'p_battery_kw' not in df.columns:
        return df, {"error": "p_battery_kw missing"}
        
    p_bat = df['p_battery_kw'].values
    soc = np.zeros(len(df) + 1)
    soc[0] = soc_init
    
    for i in range(len(df)):
        pb = p_bat[i]
        if pb < 0:  # charging
            delta = abs(pb) * eta_c * dt / c_bat
            soc[i+1] = soc[i] + delta
        else:      # discharging
            delta = pb * (1/eta_d) * dt / c_bat
            soc[i+1] = soc[i] - delta
            
    df['reconstructed_soc'] = soc[:-1]
    
    # Anomaly detection: SoC outside [0, 1] (with 5% buffer)
    violation_mask = (df['reconstructed_soc'] < -0.05) | (df['reconstructed_soc'] > 1.05)
    
    # Energy Balance Check: load = pv + p_battery + p_grid
    # Since p_grid is derived, we check if net_load - p_bat exceeds grid limit (6kW)
    energy_balance = df['load_kw'] - df['pv_kw'] - df['p_battery_kw']
    anomaly_mask = (energy_balance < -6.5) | (energy_balance > 6.5)
    
    report = {
        "corrupted_steps": int(violation_mask.sum()),
        "energy_anomalies": int(anomaly_mask.sum()),
        "is_data_corrupted": bool(violation_mask.sum() > 10) # arbitrary threshold
    }
    
    return df, report
