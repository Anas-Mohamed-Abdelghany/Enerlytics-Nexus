import pandas as pd
import numpy as np
from typing import Tuple

def detect_marubozu(Open: float, High: float, Low: float, Close: float) -> Tuple[bool, bool]:
    bullish_marubozu = False
    bearish_marubozu = False
    candle_day_movement = abs(((Close - Open) / Open) * 100) if Open != 0 else 0

    if (((Open - Low) / Open * 100 <= 1) and ((High - Close) / Close * 100 <= 1) and 1 <= candle_day_movement <= 10):
        bullish_marubozu = True
    elif (((High - Open) / Open * 100 <= 1) and ((Close - Low) / Close * 100 <= 1) and 1 <= candle_day_movement <= 10):
        bearish_marubozu = True

    return bearish_marubozu, bullish_marubozu

def analyze_marubozu(data: pd.DataFrame) -> pd.DataFrame:
    marubozu_candle_data = []
    for index, row in data.iterrows():
        Open = row['open']
        High = row['high']
        Low = row['low']
        Close = row['close']
        bear_marubozu, bull_marubozu = detect_marubozu(Open, High, Low, Close)
        if bear_marubozu:
            marubozu_candle_data.append({'Date': index, 'Type': 'Bearish Marubozu'})
        elif bull_marubozu:
            marubozu_candle_data.append({'Date': index, 'Type': 'Bullish Marubozu'})
    return pd.DataFrame(marubozu_candle_data)

def analyze_price_action(data: pd.DataFrame) -> pd.DataFrame:
    price_action_data = []
    for index, row in data.iterrows():
        Open = row['open']
        Close = row['close']
        if Open != 0 and abs(Close - Open) / Open * 100 <= 0.1:
            price_action_data.append({'Date': index, 'Pattern': 'Doji'})
    return pd.DataFrame(price_action_data)

def analyze_range_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Support'] = data['low'].rolling(window=20).min()
    data['Resistance'] = data['high'].rolling(window=20).max()
    return data

def analyze_trend_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['MA_50'] = data['close'].rolling(window=50).mean()
    data['MA_200'] = data['close'].rolling(window=200).mean()
    data['Golden_Cross'] = np.where(
        (data['MA_50'] > data['MA_200']) & (data['MA_50'].shift(1) <= data['MA_200'].shift(1)),
        True, False
    )
    data['Death_Cross'] = np.where(
        (data['MA_50'] < data['MA_200']) & (data['MA_50'].shift(1) >= data['MA_200'].shift(1)),
        True, False
    )
    return data

def analyze_position_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['MA_100'] = data['close'].rolling(window=100).mean()
    return data

def analyze_day_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Intraday_Range'] = data['high'] - data['low']
    return data

def analyze_scalping(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Small_Movement'] = np.where(data['close'].pct_change() * 100 < 0.2, True, False)
    return data

def analyze_swing_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Swing_High'] = data['high'].rolling(window=5).max()
    data['Swing_Low'] = data['low'].rolling(window=5).min()
    return data

def analyze_breakout_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Breakout_High'] = data['high'].rolling(window=20).max()
    data['Breakout_Low'] = data['low'].rolling(window=20).min()
    data['Breakout_Up'] = np.where(data['high'] > data['Breakout_High'].shift(1), True, False)
    data['Breakout_Down'] = np.where(data['low'] < data['Breakout_Low'].shift(1), True, False)
    return data

def analyze_retracement_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Retracement'] = data['close'].pct_change()
    return data

def analyze_momentum_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['Momentum'] = data['close'].diff(5)
    return data

def analyze_macd_trading(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Hist'] = data['MACD'] - data['Signal_Line']
    return data

def analyze_stock_data(data: pd.DataFrame, strategy: str) -> pd.DataFrame:
    strategies = {
        "Marubozu": analyze_marubozu,
        "Price Action": analyze_price_action,
        "Range Trading": analyze_range_trading,
        "Trend Trading": analyze_trend_trading,
        "Position Trading": analyze_position_trading,
        "Day Trading": analyze_day_trading,
        "Scalping": analyze_scalping,
        "Swing Trading": analyze_swing_trading,
        "Breakout Trading": analyze_breakout_trading,
        "Retracement Trading": analyze_retracement_trading,
        "Momentum Trading": analyze_momentum_trading,
        "MACD Trading": analyze_macd_trading,
    }
    
    if strategy not in strategies:
        raise ValueError(f"Invalid strategy selected: {strategy}")
        
    return strategies[strategy](data)

def find_best_strategy(data: pd.DataFrame) -> Tuple[str, int]:
    strategies = [
        "Marubozu", "Price Action", "Range Trading", "Trend Trading",
        "Position Trading", "Day Trading", "Scalping", "Swing Trading",
        "Breakout Trading", "Retracement Trading", "Momentum Trading", "MACD Trading"
    ]
    
    strategy_scores = {}
    
    for strategy in strategies:
        try:
            analyzed_data = analyze_stock_data(data, strategy)
            
            # Simplified scoring mechanism based on original API.py logic:
            # If the strategy returns rows of signals, count them
            if 'Date' in analyzed_data.columns and 'Pattern' in analyzed_data.columns:
                score = len(analyzed_data)
            elif 'Date' in analyzed_data.columns and 'Type' in analyzed_data.columns:
                score = len(analyzed_data)
            elif 'Golden_Cross' in analyzed_data.columns:
                score = analyzed_data['Golden_Cross'].sum() + analyzed_data['Death_Cross'].sum()
            elif 'Breakout_Up' in analyzed_data.columns:
                score = analyzed_data['Breakout_Up'].sum() + analyzed_data['Breakout_Down'].sum()
            elif 'Small_Movement' in analyzed_data.columns:
                score = analyzed_data['Small_Movement'].sum()
            else:
                score = 0
            
            strategy_scores[strategy] = int(score)
        except Exception as e:
            strategy_scores[strategy] = 0
            
    best_strategy = max(strategy_scores, key=strategy_scores.get)
    best_score = strategy_scores[best_strategy]
    
    return best_strategy, best_score
