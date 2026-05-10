import os
import sys
import pandas as pd
import numpy as np
import asyncio
import matplotlib.pyplot as plt

# Add backend to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.energy_forecaster import forecaster
from core.services.evaluation_service import compute_metrics

async def run_comparison():
    print("🚀 Starting Strategy Comparison: Static Model vs Walk-Forward Model")
    
    # 1. Load Datasets
    if not os.path.exists("../dataset_2024.csv") or not os.path.exists("../dataset_2025.csv"):
        print("❌ Error: Both dataset_2024.csv and dataset_2025.csv must exist in the root folder.")
        return

    df_2024 = pd.read_csv("../dataset_2024.csv")
    df_2025 = pd.read_csv("../dataset_2025.csv")
    
    df_2024['timestamp'] = pd.to_datetime(df_2024['timestamp'])
    df_2025['timestamp'] = pd.to_datetime(df_2025['timestamp'])
    
    df_2024 = df_2024.drop_duplicates(subset=['timestamp'])
    df_2025 = df_2025.drop_duplicates(subset=['timestamp'])
    
    df_combined = pd.concat([df_2024, df_2025]).sort_values('timestamp').drop_duplicates(subset=['timestamp'])

    print(f"📊 Loaded {len(df_2024)} rows for 2024 and {len(df_2025)} rows for 2025.")

    # ==========================================================
    # PHASE 1: THE STATIC MODEL (Trained ONLY on 2024)
    # ==========================================================
    print("\n--- 🤖 PHASE 1: STATIC MODEL (Train: 2024 only) ---")
    await forecaster.train_pipeline(df_2024)

    # Predict April 2025 (Static)
    context_april = df_combined[df_combined['timestamp'] < '2025-05-01'].copy()
    feat_ctx_april = forecaster.build_energy_features(context_april.set_index('timestamp'))
    test_feat_april = feat_ctx_april[feat_ctx_april.index.month == 4].copy()
    
    X_april = pd.DataFrame(forecaster.scaler.transform(test_feat_april[forecaster.feature_names]), columns=forecaster.feature_names)
    preds_april_static = np.maximum(0.1, forecaster.load_model.predict(X_april))
    
    actuals_april = test_feat_april['load'].values if 'load' in test_feat_april.columns else test_feat_april['load_p'].values
    valid_idx = ~np.isnan(actuals_april) & ~np.isnan(preds_april_static)
    actuals_april, preds_april_static = actuals_april[valid_idx], preds_april_static[valid_idx]
    
    metrics_april_static = compute_metrics(actuals_april, preds_april_static)
    print(f"🌸 April [Static]  NRMSE: {metrics_april_static['nrmse']:.2f}%")

    # Predict Sept 2025 (Static)
    context_sept = df_combined[df_combined['timestamp'] < '2025-10-01'].copy()
    feat_ctx_sept = forecaster.build_energy_features(context_sept.set_index('timestamp'))
    test_feat_sept = feat_ctx_sept[feat_ctx_sept.index.month == 9].copy()
    
    X_sept = pd.DataFrame(forecaster.scaler.transform(test_feat_sept[forecaster.feature_names]), columns=forecaster.feature_names)
    preds_sept_static = np.maximum(0.1, forecaster.load_model.predict(X_sept))
    
    actuals_sept = test_feat_sept['load'].values if 'load' in test_feat_sept.columns else test_feat_sept['load_p'].values
    valid_idx = ~np.isnan(actuals_sept) & ~np.isnan(preds_sept_static)
    actuals_sept, preds_sept_static = actuals_sept[valid_idx], preds_sept_static[valid_idx]
    
    metrics_sept_static = compute_metrics(actuals_sept, preds_sept_static)
    print(f"🍂 Sept  [Static]  NRMSE: {metrics_sept_static['nrmse']:.2f}%")


    # ==========================================================
    # PHASE 2: THE WALK-FORWARD MODEL (Continuous Re-training)
    # ==========================================================
    print("\n--- 🚀 PHASE 2: WALK-FORWARD MODEL (Continuous Learning) ---")
    
    import shutil
    model_dir = os.path.join(os.path.dirname(__file__), 'models')

    # Train for April (2024 + Jan-Mar 2025)
    train_april_wf = df_combined[(df_combined['timestamp'] < '2025-04-01')].copy()
    print(f"Training on historical data up to April (Rows: {len(train_april_wf)})...")
    await forecaster.train_pipeline(train_april_wf)
    
    # Save the April-specific model and scaler for the Web UI
    shutil.copy(os.path.join(model_dir, 'lgbm_load.pkl'), os.path.join(model_dir, 'lgbm_load_april.pkl'))
    shutil.copy(os.path.join(model_dir, 'scaler.pkl'), os.path.join(model_dir, 'scaler_april.pkl'))
    
    X_april_wf = pd.DataFrame(forecaster.scaler.transform(test_feat_april[forecaster.feature_names]), columns=forecaster.feature_names)
    preds_april_wf = np.maximum(0.1, forecaster.load_model.predict(X_april_wf))
    
    valid_idx = ~np.isnan(actuals_april) & ~np.isnan(preds_april_wf)
    preds_april_wf = preds_april_wf[valid_idx]
    metrics_april_wf = compute_metrics(actuals_april, preds_april_wf)
    print(f"🌸 April [Walk-Fwd] NRMSE: {metrics_april_wf['nrmse']:.2f}% (Improved by {metrics_april_static['nrmse'] - metrics_april_wf['nrmse']:.2f}%)")

    # Train for Sept (2024 + Jan-Aug 2025)
    train_sept_wf = df_combined[(df_combined['timestamp'] < '2025-09-01')].copy()
    print(f"\nRe-training on historical data up to September (Rows: {len(train_sept_wf)})...")
    await forecaster.train_pipeline(train_sept_wf)

    # Save the Sept-specific model and scaler for the Web UI
    shutil.copy(os.path.join(model_dir, 'lgbm_load.pkl'), os.path.join(model_dir, 'lgbm_load_sept.pkl'))
    shutil.copy(os.path.join(model_dir, 'scaler.pkl'), os.path.join(model_dir, 'scaler_sept.pkl'))

    X_sept_wf = pd.DataFrame(forecaster.scaler.transform(test_feat_sept[forecaster.feature_names]), columns=forecaster.feature_names)
    preds_sept_wf = np.maximum(0.1, forecaster.load_model.predict(X_sept_wf))
    
    valid_idx = ~np.isnan(actuals_sept) & ~np.isnan(preds_sept_wf)
    preds_sept_wf = preds_sept_wf[valid_idx]
    metrics_sept_wf = compute_metrics(actuals_sept, preds_sept_wf)
    print(f"🍂 Sept  [Walk-Fwd] NRMSE: {metrics_sept_wf['nrmse']:.2f}% (Improved by {metrics_sept_static['nrmse'] - metrics_sept_wf['nrmse']:.2f}%)")


    # ==========================================================
    # PHASE 3: VISUALIZATION
    # ==========================================================
    print("\n🎨 Generating Visual Comparisons...")
    
    # Plot a 3-day window in September for comparison
    zoom_len = 288 # 3 days (assuming 15min intervals)
    
    plt.figure(figsize=(15, 6))
    plt.plot(actuals_sept[:zoom_len], label='Actual Load (Ground Truth)', color='black', linewidth=2)
    plt.plot(preds_sept_static[:zoom_len], label='Static Model (Trained on 2024)', color='red', linestyle='--', alpha=0.7)
    plt.plot(preds_sept_wf[:zoom_len], label='Walk-Forward Model (Adapted to Summer)', color='green', linewidth=1.5)
    
    plt.title('September Target Window: Static vs Adaptive Walk-Forward Model')
    plt.xlabel('Timesteps (15-min intervals)')
    plt.ylabel('Load (kW)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plot_path = "../strategy_comparison.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✅ Visual comparison saved to {plot_path}")

if __name__ == "__main__":
    asyncio.run(run_comparison())
