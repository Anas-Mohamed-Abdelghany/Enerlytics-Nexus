import pandas as pd
from datetime import datetime
from typing import Dict, Union

# Italian national holidays 2024 and 2025
ITALIAN_HOLIDAYS = {
    2024: [
        '2024-01-01', '2024-01-06', '2024-03-31', '2024-04-01', # Easter Sunday/Monday
        '2024-04-25', '2024-05-01', '2024-06-02', '2024-08-15',
        '2024-11-01', '2024-12-08', '2024-12-25', '2024-12-26'
    ],
    2025: [
        '2025-01-01', '2025-01-06', '2025-04-20', '2025-04-21', # Easter Sunday/Monday
        '2025-04-25', '2025-05-01', '2025-06-02', '2025-08-15',
        '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26'
    ]
}

def is_italian_holiday(ts: Union[pd.Timestamp, datetime]) -> bool:
    date_str = ts.strftime('%Y-%m-%d')
    year = ts.year
    return date_str in ITALIAN_HOLIDAYS.get(year, [])

def get_tou_band(ts: Union[pd.Timestamp, datetime]) -> str:
    """Returns F1, F2, or F3 for Italian residential tariff"""
    h = ts.hour + ts.minute/60
    dw = ts.dayofweek  # 0=Mon, 6=Sun
    holiday = is_italian_holiday(ts)
    
    # Sunday or Holiday: all day is F3
    if dw == 6 or holiday:
        return 'F3'
    
    # Saturday
    if dw == 5:
        if 7 <= h < 23:
            return 'F2'
        return 'F3'
        
    # Weekday (Mon-Fri)
    if 8 <= h < 19:
        return 'F1'
    if (7 <= h < 8) or (19 <= h < 23):
        return 'F2'
    return 'F3'

def get_buy_price(ts: Union[pd.Timestamp, datetime]) -> float:
    """Returns the Italian ToU buy price for a given timestamp."""
    band = get_tou_band(ts)
    return {'F1': 0.2540, 'F2': 0.2682, 'F3': 0.2440}[band]
