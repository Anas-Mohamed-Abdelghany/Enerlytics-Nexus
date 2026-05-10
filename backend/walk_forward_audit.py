import os
import sys
import pandas as pd
import asyncio
import numpy as np
from datetime import datetime

# Add backend to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.energy_forecaster import forecaster
from core.services.evaluation_service import compute_metrics

async def run_walk_forward_audit(data_path="../dataset_2024.csv"):
    print("🚀 Starting Walk-Forward Validation Audit (LightGBM)...")
    
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found.")
        return

    df = pd.read_csv(data_path)
    # Ensure timestamp format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    overall_actuals = []
    overall_preds = []

    # --- 1. April Walk-Forward (Train: Jan -> Mar, Test: April) ---
    print("\n--- 🌸 APRIL AUDIT (Train: Jan-Mar, Test: April) ---")
    train_april = df[df['timestamp'].dt.month.isin([1, 2, 3])].copy()
    test_april = df[df['timestamp'].dt.month == 4].copy()

    if train_april.empty or test_april.empty:
        print("⚠️ Not enough data for April Walk-Forward.")
    else:
        print(f"Training on {len(train_april)} rows... Predicting {len(test_april)} rows...")
        await forecaster.train_pipeline(train_april)
        
        # Build features for test set using the same logic
        test_feat = forecaster.build_energy_features(test_april.set_index('timestamp'))
        
        X_test = pd.DataFrame(forecaster.scaler.transform(test_feat[forecaster.feature_names]), columns=forecaster.feature_names)
        preds = forecaster.load_model.predict(X_test)
        preds = np.maximum(0.1, preds)
        
        actuals = test_feat['load'].values if 'load' in test_feat.columns else test_feat['load_p'].values
        
        # NaN filtering
        valid_idx = ~np.isnan(actuals) & ~np.isnan(preds)
        actuals, preds = actuals[valid_idx], preds[valid_idx]
        
        metrics = compute_metrics(actuals, preds)
        print(f"✅ April NRMSE: {metrics['nrmse']:.2f}% | MAE: {metrics['mae']:.3f} | RMSE: {metrics['rmse']:.3f}")
        
        overall_actuals.extend(actuals)
        overall_preds.extend(preds)

    # --- 2. September Walk-Forward (Train: May -> Aug, Test: Sept) ---
    print("\n--- 🍂 SEPTEMBER AUDIT (Train: May-Aug, Test: Sept) ---")
    train_sept = df[df['timestamp'].dt.month.isin([5, 6, 7, 8])].copy()
    test_sept = df[df['timestamp'].dt.month == 9].copy()

    if train_sept.empty or test_sept.empty:
        print("⚠️ Not enough data for September Walk-Forward.")
    else:
        print(f"Training on {len(train_sept)} rows... Predicting {len(test_sept)} rows...")
        await forecaster.train_pipeline(train_sept)
        
        test_feat = forecaster.build_energy_features(test_sept.set_index('timestamp'))
        X_test = pd.DataFrame(forecaster.scaler.transform(test_feat[forecaster.feature_names]), columns=forecaster.feature_names)
        preds = forecaster.load_model.predict(X_test)
        preds = np.maximum(0.1, preds)
        
        actuals = test_feat['load'].values if 'load' in test_feat.columns else test_feat['load_p'].values
        
        # NaN filtering
        valid_idx = ~np.isnan(actuals) & ~np.isnan(preds)
        actuals, preds = actuals[valid_idx], preds[valid_idx]
        
        metrics = compute_metrics(actuals, preds)
        print(f"✅ September NRMSE: {metrics['nrmse']:.2f}% | MAE: {metrics['mae']:.3f} | RMSE: {metrics['rmse']:.3f}")
        
        overall_actuals.extend(actuals)
        overall_preds.extend(preds)

    # --- Overall Score ---
    if overall_actuals:
        overall_metrics = compute_metrics(np.array(overall_actuals), np.array(overall_preds))
        print("\n🏆 --- FINAL WALK-FORWARD SCORECARD ---")
        print(f"Aggregate NRMSE: {overall_metrics['nrmse']:.2f}%")
        print("Note: This model was dynamically re-trained to adapt to seasonaldrift!")

if __name__ == "__main__":
    asyncio.run(run_walk_forward_audit())
