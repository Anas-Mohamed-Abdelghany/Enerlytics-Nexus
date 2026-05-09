import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_squared_error, mean_absolute_error
from .feature_service import build_features

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes core forecasting accuracy metrics: RMSE, MAE, and NRMSE.
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    # Normalized RMSE using mean of true values
    mean_true = np.mean(y_true)
    nrmse = (rmse / mean_true * 100) if mean_true != 0 else 0.0
    
    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "nrmse": float(nrmse)
    }

def evaluate_on_surprise_dataset(forecaster: Any, surprise_df: pd.DataFrame, site1_nrmse: float) -> float:
    """
    Evaluates model generalization on a completely new residential site (surprise set).
    Checks for performance degradation without retraining.
    """
    # 1. Build features using original site's logic
    X_surprise, y_surprise, _ = build_features(surprise_df, is_training=False)
    
    # 2. Inference (No retraining!)
    y_pred = forecaster.predict(X_surprise)
    
    # 3. Compute Metrics
    metrics = compute_metrics(y_surprise.values, y_pred)
    surprise_nrmse = metrics['nrmse']
    
    # 4. Generalization Analysis
    ratio = surprise_nrmse / site1_nrmse if site1_nrmse > 0 else 1.0
    status = "Good Generalization" if ratio < 1.3 else "High Degradation"
    
    print("\n" + "="*40)
    print("SURPRISE DATASET EVALUATION")
    print("-" * 40)
    print(f"Site 1 NRMSE:     {site1_nrmse:.2f}%")
    print(f"Surprise NRMSE:   {surprise_nrmse:.2f}%")
    print(f"Degradation Ratio: {ratio:.2f}x")
    print(f"Status:           {status}")
    print("="*40 + "\n")
    
    return surprise_nrmse
