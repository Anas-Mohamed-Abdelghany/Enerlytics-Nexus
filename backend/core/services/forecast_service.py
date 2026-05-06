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
    
    # Calculate training score using same logic as validation (Inverse-MAPE) for consistency
    train_predictions = model.predict(X_train, verbose=0)
    if prediction_type == 'classification':
        actuals = np.argmax(y_train, axis=1)
        preds = np.argmax(train_predictions, axis=1)
        training_score = round(float(np.mean(actuals == preds) * 100), 1)
    else:
        # Inverse transform to get real price comparison
        actual_prices = target_scaler.inverse_transform(y_train.reshape(-1, 1)).flatten()
        pred_prices = target_scaler.inverse_transform(train_predictions.reshape(-1, 1)).flatten()
        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            mape = np.mean(np.abs((actual_prices - pred_prices) / actual_prices))
        training_score = round(max(0, 100 * (1 - mape)), 1)
        
    return model, scaler, target_scaler, features_to_use, training_score

def validate_model(model, data, features, scaler, target_scaler, prediction_type, lookback=60, samples=5, start_idx=None, end_idx=None):
    """
    Performs a mini-backtest on historical segments to calculate a score.
    If start_idx and end_idx are provided, it only picks samples from that specific range.
    """
    import random
    s_idx = start_idx if start_idx is not None else lookback
    e_idx = end_idx if end_idx is not None else len(data)
    
    if e_idx <= s_idx: return 0.0, []
    
    scores = []
    details = []
    # Pick random indices from the specified range
    available_indices = list(range(max(lookback, s_idx), e_idx))
    if not available_indices: return 0.0, []
    
    # If samples is None, take everything in the range
    num_to_take = min(samples, len(available_indices)) if samples is not None else len(available_indices)
    indices = random.sample(available_indices, num_to_take)
    
    # Sort indices so validation details are in chronological order
    indices.sort()
    
    for idx in indices:
        # Prepare input
        input_data = data[features].iloc[idx-lookback:idx]
        scaled_input = scaler.transform(input_data).reshape(1, lookback, len(features))
        
        # Predict
        prediction = model.predict(scaled_input, verbose=0)
        ts = data['timestamp'].iloc[idx]
        
        if prediction_type == 'regression':
            actual = float(data['Close'].iloc[idx])
            pred_val = float(target_scaler.inverse_transform(prediction.reshape(-1, 1))[0, 0])
            error = abs(actual - pred_val) / actual
            scores.append(max(0, 1 - error))
            details.append({"timestamp": ts, "actual": round(actual, 2), "predicted": round(pred_val, 2)})
        else:
            actual = int(data['Target'].iloc[idx])
            pred_class = int(np.argmax(prediction, axis=1)[0])
            scores.append(1.0 if actual == pred_class else 0.0)
            labels = {0: "DOWN", 1: "STABLE", 2: "UP"}
            details.append({"timestamp": ts, "actual": labels.get(actual), "predicted": labels.get(pred_class)})
            
    avg_score = round(float(np.mean(scores) * 100), 1) if scores else 0.0
    return avg_score, details

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
    use_bidirectional: bool = True,
    check_samples: int = 5
) -> Dict[str, Any]:
    
    if len(series) < 61:
        raise ValueError("Not enough historical data to train the LSTM model. At least 61 data points are required.")
        
    df = pd.DataFrame([p.model_dump() for p in series])
    df = add_technical_indicators(df)
    
    if prediction_type == 'classification':
        df = create_classification_labels(df)
        
    lookback = 60
    
    # Split data: 90% Training, 10% Validation (Latest data, strictly unseen)
    split_idx = int(len(df) * 0.9)
    train_df = df.iloc[:split_idx].copy()
    
    # Train only on training set
    model, scaler, target_scaler, features, training_score = build_and_train_model(train_df, prediction_type, use_bidirectional, lookback)
    
    # 1. Validation Score: Run on ALL points in the strictly unseen 10% (Latest data)
    validation_score, val_details = validate_model(model, df, features, scaler, target_scaler, prediction_type, lookback, samples=None, start_idx=split_idx)
    for d in val_details: d['type'] = 'VALIDATION'
    
    # 2. Check Score: Run on the user-specified number of samples from training data (Robustness check)
    check_score, check_details = validate_model(model, df, features, scaler, target_scaler, prediction_type, lookback, samples=check_samples, start_idx=lookback, end_idx=split_idx)
    for d in check_details: d['type'] = 'CHECK'
    
    # Merge details for UI
    all_validation_details = sorted(val_details + check_details, key=lambda x: x['timestamp'])
    
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
            "feature_importance": importance,
            "validation_score": validation_score,
            "check_score": check_score,
            "training_score": training_score,
            "validation_details": all_validation_details
        }
    else:
        pred_class = predict_future(model, df, features, scaler, target_scaler, 'classification', lookback, horizon_days)
        labels = {0: "DOWN", 1: "STABLE", 2: "UP"}
        return {
            "type": "classification",
            "market": market,
            "horizon_hours": horizon_days * 24,
            "prediction": labels.get(pred_class, "UNKNOWN"),
            "feature_importance": importance,
            "validation_score": validation_score,
            "check_score": check_score,
            "training_score": training_score,
            "validation_details": all_validation_details
        }
