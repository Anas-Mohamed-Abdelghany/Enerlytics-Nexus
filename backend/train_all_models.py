import os
import pandas as pd
import asyncio
import sys

# Add backend to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.energy_forecaster import forecaster
from core.services.lstm_forecaster import generate_lstm_forecast_logic
from models.schemas import OHLCVPoint

async def train_all():
    print("🚀 Starting Multi-Architecture Training Pipeline...")
    
    # 1. Load Dataset
    data_path = "dataset_2024.csv"
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found. Please ensure your training data is in the backend folder.")
        return

    df = pd.read_csv(data_path)
    print(f"📈 Loaded {len(df)} samples from {data_path}")

    # 2. Train LightGBM (Advanced)
    print("\n--- Training Architecture: LightGBM (Advanced) ---")
    try:
        # Prepare data for forecaster
        # It expects a list of dicts or a DF depending on how it's called
        lgbm_results = await forecaster.train_pipeline(df)
        print(f"✅ LightGBM Trained. RMSE: {lgbm_results.get('load_rmse', 'N/A')}")
    except Exception as e:
        print(f"❌ LightGBM Training Failed: {e}")

    # 3. Train Standard LSTM
    print("\n--- Training Architecture: Standard LSTM ---")
    try:
        # Convert DF to list of OHLCV points as expected by the service
        # Note: We map load_p to close for the LSTM service
        points = []
        for _, row in df.iterrows():
            points.append(OHLCVPoint(
                timestamp=int(pd.to_datetime(row['timestamp']).timestamp() * 1000),
                open=row.get('load_p', 0),
                high=row.get('load_p', 0),
                low=row.get('load_p', 0),
                close=row.get('load_p', 0),
                volume=0
            ))
        
        generate_lstm_forecast_logic(
            market="Audit-Standard",
            series=points,
            horizon_days=1,
            prediction_type="regression",
            architecture="standard"
        )
        print("✅ Standard LSTM Trained and Saved.")
    except Exception as e:
        print(f"❌ Standard LSTM Training Failed: {e}")

    # 4. Train Bidirectional LSTM
    print("\n--- Training Architecture: Bidirectional LSTM ---")
    try:
        generate_lstm_forecast_logic(
            market="Audit-Bidi",
            series=points,
            horizon_days=1,
            prediction_type="regression",
            architecture="bidirectional"
        )
        print("✅ Bidirectional LSTM Trained and Saved.")
    except Exception as e:
        print(f"❌ Bidirectional LSTM Training Failed: {e}")

    print("\n🎉 All models trained and saved to 'models/' directory.")

if __name__ == "__main__":
    asyncio.run(train_all())
