import os
import sys
import pandas as pd
import numpy as np
import asyncio
import matplotlib.pyplot as plt
import joblib

# Add backend to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.energy_forecaster import forecaster

async def predict_2026():
    print("🔮 Starting 2026 Energy Load Forecast Pipeline")
    
    # 1. Load the Pre-Merged Dataset
    merged_csv_path = "../merged_dataset.csv"
    if not os.path.exists(merged_csv_path):
        print(f"❌ Error: {merged_csv_path} not found. Please provide the merged CSV file.")
        return

    print(f"📊 Loading pre-merged historical data from {merged_csv_path}...")
    df_combined = pd.read_csv(merged_csv_path)
    df_combined['timestamp'] = pd.to_datetime(df_combined['timestamp'])
    df_combined = df_combined.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
    
    print(f"✅ Dataset loaded: {len(df_combined)} rows.")


    # 2. Validation Phase (Check Accuracy on a hold-out set)
    print("\n🧪 PHASE 1: Validation (Checking model accuracy)...")
    # Split: 85% train, 15% test
    split_idx = int(len(df_combined) * 0.85)
    train_data = df_combined.iloc[:split_idx]
    test_data = df_combined.iloc[split_idx:]
    
    # Train validation model
    await forecaster.train_pipeline(train_data)
    
    # Predict on test set
    test_feat = forecaster.build_energy_features(test_data.set_index('timestamp'))
    X_test_scaled = forecaster.scaler.transform(test_feat[forecaster.feature_names])
    test_preds = forecaster.load_model.predict(X_test_scaled)
    test_actuals = test_feat['load'].values if 'load' in test_feat.columns else test_feat['load_p'].values
    
    # Calculate Metrics
    from core.services.evaluation_service import compute_metrics
    metrics = compute_metrics(test_actuals, test_preds)
    
    print("-" * 40)
    print(f"📊 VALIDATION ACCURACY (85/15 Split):")
    print(f"   - RMSE:  {metrics['rmse']:.4f} kW")
    print(f"   - MAE:   {metrics['mae']:.4f} kW")
    print(f"   - NRMSE: {metrics['nrmse']:.2f}%")
    print("-" * 40)

    # 3. Final Training on All Available Data
    print("\n🤖 PHASE 2: Final Training on the full historical dataset...")
    await forecaster.train_pipeline(df_combined)
    print("✅ Full model training complete.")


    # 3. Generate 2026 Prediction Window (First Week)
    print("📅 Generating prediction window: Jan 1st - Jan 7th, 2026...")
    future_start = pd.Timestamp('2026-01-01 00:00:00')
    future_end = pd.Timestamp('2026-01-07 23:45:00')
    future_index = pd.date_range(start=future_start, end=future_end, freq='15min')
    
    # Create a placeholder dataframe for 2026 using the EXACT same column names as training data
    # to avoid duplicates during renaming
    cols = list(df_combined.columns)
    if 'timestamp' in cols: cols.remove('timestamp')
    
    df_2026 = pd.DataFrame(index=future_index, columns=cols)
    df_2026.index.name = 'timestamp'
    
    # To calculate features (lags, technical indicators), we need context
    last_context = df_combined.tail(2000).set_index('timestamp')
    
    # Combine context with future window
    context_with_future = pd.concat([last_context, df_2026])
    
    # 4. Feature Engineering for 2026
    print("🛠 Engineering features for 2026...")
    # Fill future placeholders with last known values to provide a baseline for indicators
    context_with_future = context_with_future.ffill()
    
    # Ensure no duplicates (safety check)
    context_with_future = context_with_future.loc[:, ~context_with_future.columns.duplicated()]

    feat_df = forecaster.build_energy_features(context_with_future)

    
    # Slice only the 2026 part
    X_2026_feat = feat_df[feat_df.index >= future_start].copy()
    
    # 5. Execute Prediction
    print("🚀 Generating forecast...")
    X_scaled = forecaster.scaler.transform(X_2026_feat[forecaster.feature_names])
    X = pd.DataFrame(X_scaled, columns=forecaster.feature_names)
    
    preds_2026 = forecaster.load_model.predict(X)
    # Ensure no negative load
    preds_2026 = np.maximum(0.05, preds_2026)

    # 6. Save and Visualize
    # Format timestamp to match image: m/d/yyyy H:MM (no leading zeros)
    # Using a list comprehension for precise formatting across platforms
    formatted_ts = [f"{ts.month}/{ts.day}/{ts.year} {ts.hour}:{ts.minute:02d}" for ts in X_2026_feat.index]

    results_df = pd.DataFrame({
        'timestamp': formatted_ts,
        'load_p': preds_2026
    })
    
    results_csv = "forecast_2026_week1.csv"
    results_df.to_csv(results_csv, index=False)
    print(f"✅ Forecast saved to {results_csv} with 2 columns.")


    plt.figure(figsize=(15, 6))
    plt.plot(X_2026_feat.index, preds_2026, color='#00ff9d', linewidth=2, label='Predicted Load 2026')
    plt.fill_between(X_2026_feat.index, preds_2026*0.9, preds_2026*1.1, color='#00ff9d', alpha=0.1, label='Confidence Interval (est)')

    
    plt.title('Enerlytics Nexus: 2026 Energy Load Forecast (First Week)', color='white', fontsize=14)
    plt.xlabel('Date', color='white')
    plt.ylabel('Load (kW)', color='white')
    plt.grid(True, alpha=0.2, color='white')
    plt.legend()
    
    # Styling for dark theme
    plt.gcf().set_facecolor('#1a1a1a')
    plt.gca().set_facecolor('#1a1a1a')
    plt.gca().tick_params(colors='white')
    for spine in plt.gca().spines.values():
        spine.set_color('white')

    plot_path = "forecast_2026_viz.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"📈 Visualization saved to {plot_path}")

if __name__ == "__main__":
    asyncio.run(predict_2026())
