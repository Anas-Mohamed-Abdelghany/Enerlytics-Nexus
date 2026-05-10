import os
import sys
import pandas as pd
import numpy as np
import asyncio
import matplotlib.pyplot as plt
import joblib
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMRegressor

# Add current directory to path to import local services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.energy_forecaster import forecaster
from core.services.evaluation_service import compute_metrics

async def run_march_task():
    print("🚀 Enerlytics Nexus: March 2026 Validation & Comparison Task")
    print("-" * 50)

    # 1. Paths (Looking in the project root)
    train_csv = "../2nd_DataSet.csv"
    test_csv = "../2nd_Forcast.csv"

    if not os.path.exists(train_csv) or not os.path.exists(test_csv):
        print(f"❌ Error: Required files ({train_csv} or {test_csv}) not found in directory.")
        return

    # 2. Loading Data
    print(f"📊 Loading Training Data: {train_csv}")
    df_train = pd.read_csv(train_csv)
    df_train['timestamp'] = pd.to_datetime(df_train['timestamp'])
    
    print(f"📊 Loading Test/Forecast Data: {test_csv}")
    df_test = pd.read_csv(test_csv)
    df_test['timestamp'] = pd.to_datetime(df_test['timestamp'])
    df_test = df_test.sort_values('timestamp')

    # --- PHASE 1: EVALUATE LEGACY MODEL ---
    print("\n📦 Step 1: Evaluating EXISTING Production Model (.pkl)...")
    
    # Save the legacy model state before retraining
    legacy_model = forecaster.load_model
    legacy_scaler = forecaster.scaler
    
    # Prepare test features (Lags need context)
    # We use a larger context from training to ensure feature alignment
    context_df = df_train.tail(2000).copy()
    full_test_context = pd.concat([context_df, df_test]).set_index('timestamp')
    
    # Standardize columns if they have the _p suffix
    if 'load_p' in full_test_context.columns and 'load' not in full_test_context.columns:
        full_test_context = full_test_context.rename(columns={'load_p': 'load'})
    if 'pv_p' in full_test_context.columns and 'solar' not in full_test_context.columns:
        full_test_context = full_test_context.rename(columns={'pv_p': 'solar'})

    feat_df = forecaster.build_energy_features(full_test_context)
    X_test_feat = feat_df[feat_df.index >= df_test['timestamp'].min()].copy()
    
    # Identify the correct 'load' column for ground truth
    actuals = X_test_feat['load'].values if 'load' in X_test_feat.columns else X_test_feat['load_p'].values

    # Legacy Prediction
    X_legacy_scaled = legacy_scaler.transform(X_test_feat[forecaster.feature_names])
    legacy_preds = legacy_model.predict(X_legacy_scaled)
    legacy_metrics = compute_metrics(actuals, legacy_preds)

    # --- PHASE 2: TRAIN & EVALUATE NEW MODEL ---
    print("\n🤖 Step 2: Training NEW Model (In-Memory Only)...")
    
    # We perform a manual training loop here to avoid overwriting your production .pkl files
    X_train_feat = forecaster.build_energy_features(df_train.set_index('timestamp'))
    train_features = forecaster.feature_names
    
    X_train = X_train_feat[train_features]
    y_train = X_train_feat['load']
    
    # Fit a fresh scaler for the new data
    new_scaler = StandardScaler()
    X_train_scaled = new_scaler.fit_transform(X_train)
    
    # Train fresh LightGBM
    new_model = LGBMRegressor(n_estimators=100, learning_rate=0.05, verbose=-1)
    new_model.fit(X_train_scaled, y_train)
    
    # New Prediction for March
    X_new_scaled = new_scaler.transform(X_test_feat[train_features])
    new_preds = new_model.predict(X_new_scaled)
    new_metrics = compute_metrics(actuals, new_preds)

    # --- PHASE 3: COMPARISON ---
    print("\n" + "="*50)
    print("📊 MODEL COMPARISON: MARCH 2026 WINDOW")
    print("-" * 50)
    print(f"   METRIC    |  LEGACY PKL  |  RETRAINED   |  IMPROVEMENT")
    print(f"   RMSE      |  {legacy_metrics['rmse']:.4f}     |  {new_metrics['rmse']:.4f}     |  {((legacy_metrics['rmse']-new_metrics['rmse'])/legacy_metrics['rmse']*100):.1f}%")
    print(f"   MAE       |  {legacy_metrics['mae']:.4f}     |  {new_metrics['mae']:.4f}     |  {((legacy_metrics['mae']-new_metrics['mae'])/legacy_metrics['mae']*100):.1f}%")
    print(f"   NRMSE     |  {legacy_metrics['nrmse']:.2f}%     |  {new_metrics['nrmse']:.2f}%     |  {(legacy_metrics['nrmse']-new_metrics['nrmse']):.2f} pts")
    print("="*50)

    # 7. Save Results CSV
    results_df = pd.DataFrame({
        'timestamp': X_test_feat.index,
        'actual_load': actuals,
        'legacy_pred': legacy_preds,
        'new_pred': new_preds
    })
    results_df.to_csv("march_2026_comparison_results.csv", index=False)

    # 8. Visualization
    print("\n📈 Generating comparison plot...")
    plt.figure(figsize=(15, 8))
    plot_slice = 24 * 4 * 7 # 1 week
    
    plt.plot(results_df['timestamp'][:plot_slice], results_df['actual_load'][:plot_slice], 
             color='#ffffff', alpha=0.4, label='Actual Load (Ground Truth)', linewidth=1.5)
    plt.plot(results_df['timestamp'][:plot_slice], results_df['legacy_pred'][:plot_slice], 
             color='#ff4d4d', label=f'Legacy Model (NRMSE: {legacy_metrics["nrmse"]:.1f}%)', linewidth=1, linestyle='--')
    plt.plot(results_df['timestamp'][:plot_slice], results_df['new_pred'][:plot_slice], 
             color='#00ff9d', label=f'Retrained Model (NRMSE: {new_metrics["nrmse"]:.1f}%)', linewidth=2)

    plt.title('March 2026 Forecast Duel: Legacy vs Retrained Model', color='white', fontsize=14, pad=20)
    plt.gcf().set_facecolor('#0d1018')
    plt.gca().set_facecolor('#0d1018')
    plt.gca().tick_params(colors='white')
    plt.legend(facecolor='#1a1a1a', labelcolor='white')
    
    plt.savefig("march_2026_comparison_duel.png", dpi=300, bbox_inches='tight')
    print(f"🖼 Comparison plot saved to: march_2026_comparison_duel.png")

if __name__ == "__main__":
    asyncio.run(run_march_task())
