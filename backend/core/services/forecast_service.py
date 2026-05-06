import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import timedelta
from typing import List, Any, Dict, Optional

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, Input
from tensorflow.keras.utils import to_categorical

from models.schemas import ForecastResponse, ForecastPoint, OHLCVPoint

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Rename columns to match pandas_ta expectations
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    
    # Calculate indicators directly to avoid pandas_ta Strategy bugs
    df.ta.macd(append=True)
    df.ta.rsi(append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.atr(append=True)
    df.ta.stoch(append=True)
    df.ta.adx(append=True)
    df.ta.willr(append=True)
    df.ta.obv(append=True)
    
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    df['Golden_Cross'] = (df['MA50'] > df['MA200']) & (df['MA50'].shift(1) <= df['MA200'].shift(1))
    df['Death_Cross'] = (df['MA50'] < df['MA200']) & (df['MA50'].shift(1) >= df['MA200'].shift(1))
    
    # Do not dropna() here, or we lose all data if the user queries < 200 days
    # Instead, forward fill and back fill missing values
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    # Fill remaining NaNs with 0 (e.g., categorical/boolean columns if any)
    df = df.infer_objects(copy=False)
    df.fillna(0, inplace=True)
    return df

def create_classification_labels(df: pd.DataFrame, look_forward=1, threshold=0.001) -> pd.DataFrame:
    df['future_close'] = df['Close'].shift(-look_forward)
    df['pct_change'] = (df['future_close'] - df['Close']) / df['Close']
    
    df['Target'] = 1 # Stable
    df.loc[df['pct_change'] > threshold, 'Target'] = 2 # Up
    df.loc[df['pct_change'] < -threshold, 'Target'] = 0 # Down
    
    df.drop(['future_close', 'pct_change'], axis=1, inplace=True)
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    return df

def build_and_train_model(data: pd.DataFrame, prediction_type: str, use_bidirectional: bool, lookback: int = 60):
    features_to_use = [col for col in data.columns if col not in ['Open','High','Low','MA50','MA200','Golden_Cross','Death_Cross','Target', 'timestamp']]
    
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data[features_to_use])
    
    X_train, y_train = [], []
    target_scaler = None
    
    if prediction_type == 'regression':
        target_scaler = MinMaxScaler(feature_range=(0,1))
        scaled_target = target_scaler.fit_transform(data[['Close']])
        for i in range(lookback, len(scaled_data)):
            X_train.append(scaled_data[i-lookback:i])
            y_train.append(scaled_target[i, 0])
    else:
        target_data = to_categorical(data['Target'], num_classes=3)
        for i in range(lookback, len(scaled_data)):
            X_train.append(scaled_data[i-lookback:i])
            y_train.append(target_data[i])

    X_train, y_train = np.array(X_train), np.array(y_train)

    model = Sequential()
    model.add(Input(shape=(X_train.shape[1], X_train.shape[2])))
    lstm_layer = LSTM(units=100, return_sequences=True)
    if use_bidirectional: model.add(Bidirectional(lstm_layer))
    else: model.add(lstm_layer)
    model.add(Dropout(0.2))
    model.add(LSTM(units=100, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=50))
    
    if prediction_type == 'regression':
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
    else:
        model.add(Dense(units=3, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
    print(f"Starting LSTM training for {prediction_type} ({len(X_train)} samples, 10 epochs)...")
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)
    print("LSTM training complete.")
    return model, scaler, target_scaler, features_to_use

def predict_future(model, data, features_to_use, scaler, target_scaler, prediction_type, lookback=60, future_days=30):
    last_lookback_days = data[features_to_use][-lookback:]
    scaled_inputs = scaler.transform(last_lookback_days)
    
    if prediction_type == 'regression':
        predictions = []
        current_batch = scaled_inputs.reshape(1, lookback, len(features_to_use))
        for _ in range(future_days):
            predicted_scaled_val = model.predict(current_batch, verbose=0)[0]
            predictions.append(predicted_scaled_val)
            new_row = current_batch[0, -1, :].copy()
            close_idx = features_to_use.index('Close')
            new_row[close_idx] = predicted_scaled_val
            next_batch_2d = np.append(current_batch[0, 1:, :], [new_row], axis=0)
            current_batch = next_batch_2d.reshape(1, lookback, len(features_to_use))
        return target_scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    else:
        current_batch = scaled_inputs.reshape(1, lookback, len(features_to_use))
        prediction = model.predict(current_batch, verbose=0)
        return int(np.argmax(prediction, axis=1)[0])

def generate_lstm_forecast(
    market: str, 
    series: List[OHLCVPoint], 
    horizon_days: int = 30,
    prediction_type: str = "regression",
    use_bidirectional: bool = True
) -> Dict[str, Any]:
    
    if len(series) < 61:
        raise ValueError("Not enough historical data to train the LSTM model. At least 61 data points are required.")
        
    df = pd.DataFrame([p.model_dump() for p in series])
    df = add_technical_indicators(df)
    
    if prediction_type == 'classification':
        df = create_classification_labels(df)
        
    lookback = 60
    model, scaler, target_scaler, features = build_and_train_model(df, prediction_type, use_bidirectional, lookback)
    
    last_timestamp = pd.to_datetime(series[-1].timestamp, unit="ms", utc=True)
    
    # Calculate simple correlation-based feature importance (Non-fake)
    import numpy as np
    with np.errstate(divide='ignore', invalid='ignore'):
        correlations = df[features].corrwith(df['Target' if prediction_type == 'classification' else 'Close']).abs().fillna(0)
    total_corr = correlations.sum()
    importance = (correlations / total_corr).to_dict() if total_corr > 0 else {k: 0.0 for k in features}
    # Format keys for UI
    importance = {k.replace('_', ' '): round(float(v), 2) for k, v in importance.items() if v > 0.01}
    # Keep top 5
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5])

    if prediction_type == 'regression':
        forecast_prices = predict_future(model, df, features, scaler, target_scaler, 'regression', lookback, horizon_days)
        points: List[ForecastPoint] = []
        for i, price in enumerate(forecast_prices):
            ts = last_timestamp + timedelta(days=i + 1)
            # Use volatility-based CI instead of fixed 5% (More realistic)
            volatility = df['Close'].pct_change().std() * np.sqrt(i+1)
            lower = float(price * (1 - 2*volatility))
            upper = float(price * (1 + 2*volatility))
            points.append(ForecastPoint(timestamp=ts, forecast=float(price), lower_ci=round(lower, 2), upper_ci=round(upper, 2)))
        return {
            "type": "regression",
            "market": market,
            "horizon_hours": horizon_days * 24,
            "points": [p.model_dump() for p in points],
            "feature_importance": importance
        }
    else:
        pred_class = predict_future(model, df, features, scaler, target_scaler, 'classification', lookback, horizon_days)
        labels = {0: "DOWN", 1: "STABLE", 2: "UP"}
        return {
            "type": "classification",
            "market": market,
            "horizon_hours": horizon_days * 24,
            "prediction": labels.get(pred_class, "UNKNOWN"),
            "feature_importance": importance
        }
