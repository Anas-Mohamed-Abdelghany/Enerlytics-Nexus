import io
import os
import requests
import pandas as pd
import json
from typing import Optional

from models.schemas import UploadResponse
from core.services.upload_service import _normalise_df, _compute_kpis

# Load keys from JSON config if available
def _load_config():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "api_keys.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

_CONFIG = _load_config()

# Load ticker mapping from JSON
def _load_ticker_map():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "ticker_mapping.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

_TICKER_MAP = _load_ticker_map()

def get_ticker_mapping():
    return _TICKER_MAP

# Priority: Environment Var > JSON Config > Hardcoded Fallback
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", _CONFIG.get("ALPHA_VANTAGE_API_KEY", "05ZYZ70H6F5L9II9"))
FMP_API_KEY = os.getenv("FMP_API_KEY", _CONFIG.get("FMP_API_KEY", "bhZYEjY4PaWmDaM2I35GEInihiWq3Htf"))
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", _CONFIG.get("POLYGON_API_KEY", "0kurlMvit3vtYmKSSepicYws1zvpdkTY"))
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", _CONFIG.get("TWELVE_DATA_API_KEY", "ff69818c7b134877abcf08807de4367c"))
EOD_API_KEY = os.getenv("EOD_API_KEY", _CONFIG.get("EOD_API_KEY", "68457dd194b332.71068275"))
EMBER_API_KEY = os.getenv("EMBER_API_KEY", _CONFIG.get("EMBER_API_KEY", "ee854030-06e0-fae3-726a-0cfb7d66c08b"))
ENERGY_PRICE_API_KEY = os.getenv("ENERGY_PRICE_API_KEY", _CONFIG.get("ENERGY_PRICE_API_KEY", "cc367b72778d688434fd127515007a08"))
METAL_PRICE_API_KEY = os.getenv("METAL_PRICE_API_KEY", _CONFIG.get("METAL_PRICE_API_KEY", "8267fd1602aeb2a9f412fcf2729e4daa"))
FOREX_RATE_API_KEY = os.getenv("FOREX_RATE_API_KEY", _CONFIG.get("FOREX_RATE_API_KEY", "e39dc69cf0e81ca185b1b52732f76ad3"))
EIA_API_KEY = os.getenv("EIA_API_KEY", _CONFIG.get("EIA_API_KEY", ""))

def fetch_alpha_vantage(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or ALPHA_VANTAGE_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={key}&outputsize=full&datatype=csv"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from Alpha Vantage. HTTP {response.status_code}")
        
    df = pd.read_csv(io.StringIO(response.text))
    
    if 'timestamp' not in df.columns:
        error_msg = response.text[:200]
        raise Exception(f"Alpha Vantage API error: {error_msg}")
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'] >= pd.to_datetime(start_date)) & (df['timestamp'] <= pd.to_datetime(end_date))]
    
    if df.empty: raise ValueError(f"No data found for {ticker} in the specified date range from Alpha Vantage.")
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_AlphaVantage", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_fmp(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or FMP_API_KEY
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={key}"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Failed to fetch data from FMP. HTTP {response.status_code}")
        
    json_data = response.json()
    if 'historical' not in json_data: raise Exception(f"Invalid response format from FMP or missing data for {ticker}.")
        
    df = pd.DataFrame(json_data['historical'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
    
    if df.empty: raise ValueError(f"No data found for {ticker} in the specified date range from FMP.")
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_FMP", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_polygon(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or POLYGON_API_KEY
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={key}"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Failed to fetch data from Polygon. HTTP {response.status_code}")
    
    json_data = response.json()
    if 'results' not in json_data: raise Exception(f"Invalid response from Polygon: {json_data.get('error', 'No results')}")
        
    df = pd.DataFrame(json_data['results'])
    df.rename(columns={'o':'open','h':'high','l':'low','c':'close','v':'volume','t':'timestamp'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_Polygon", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_twelve_data(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or TWELVE_DATA_API_KEY
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&start_date={start_date}&end_date={end_date}&apikey={key}&outputsize=5000"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Failed to fetch data from Twelve Data. HTTP {response.status_code}")
    
    json_data = response.json()
    if 'values' not in json_data: raise Exception(f"Invalid response from Twelve Data: {json_data.get('message', 'No values')}")
        
    df = pd.DataFrame(json_data['values'])
    df.rename(columns={'datetime': 'timestamp'}, inplace=True)
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_TwelveData", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_eod(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or EOD_API_KEY
    url = f"https://eodhistoricaldata.com/api/eod/{ticker}.US?from={start_date}&to={end_date}&api_token={key}&period=d&fmt=json"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Failed to fetch data from EOD. HTTP {response.status_code}")
    
    try:
        json_data = response.json()
    except:
        raise Exception(f"Failed to parse EOD response: {response.text[:100]}")
        
    df = pd.DataFrame(json_data)
    if df.empty: raise ValueError(f"No data found from EOD for {ticker}")
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_EOD", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_ember(entity_code: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or EMBER_API_KEY
    if not key: raise Exception("Ember API Key is missing. Please add it to config/api_keys.json")
    
    start_year = start_date[:4]
    end_year = end_date[:4]
    
    url = f"https://api.ember-energy.org/v1/electricity-generation/yearly?entity_code={entity_code}&start_date={start_year}&end_date={end_year}&api_key={key}"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ember API Error: {response.status_code} - {response.text}")
        
    res_json = response.json()
    data = res_json.get('data', [])
    if not data:
        raise Exception(f"No Ember data found for {entity_code} in the specified range.")
        
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['date'], format='%Y')
    
    # Ember data provides multiple series (fuel types) per year.
    # We aggregate to get the Total Generation (TWh) per year.
    agg_df = df.groupby('timestamp')['generation_twh'].sum().reset_index()
    agg_df.rename(columns={'generation_twh': 'close'}, inplace=True)
    agg_df['open'] = agg_df['close']
    agg_df['high'] = agg_df['close']
    agg_df['low'] = agg_df['close']
    agg_df['volume'] = 0
    
    series = _normalise_df(agg_df)
    return UploadResponse(filename=f"{entity_code}_Ember_Generation", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_energi_data_service(dataset: str, start_date: str, end_date: str) -> UploadResponse:
    url = f"https://api.energidataservice.dk/dataset/{dataset}?start={start_date}&end={end_date}&limit=5000"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Energi Data Service Error: {response.status_code}")
        
    records = response.json().get('records', [])
    if not records:
        raise Exception(f"No records found for dataset {dataset} in range {start_date} to {end_date}")
        
    df = pd.DataFrame(records)
    
    # Robust column identification
    time_col = next((c for c in df.columns if 'UTC' in c or 'DK' in c or 'date' in c.lower()), None)
    if not time_col: raise Exception("Timestamp column not found in dataset")
    df['timestamp'] = pd.to_datetime(df[time_col])
    
    # Identify value column (skip time, strings like PriceArea)
    val_col = None
    for c in df.columns:
        if c == 'timestamp' or c == time_col or 'Area' in c or 'Code' in c: continue
        try:
            df[c] = pd.to_numeric(df[c])
            val_col = c
            break
        except: continue
        
    if not val_col: raise Exception("Numeric data column not found in dataset")
    
    df.rename(columns={val_col: 'close'}, inplace=True)
    df['open'] = df['close']
    df['high'] = df['close']
    df['low'] = df['close']
    df['volume'] = 0
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{dataset}_EnergiDK", rows=len(series), series=series, kpis=_compute_kpis(series))

# ── Twelve Data Utilities ───────────────────────────────────────────────────
def get_twelve_data_exchange_rate(symbol: str, api_key: str = None) -> dict:
    key = api_key or TWELVE_DATA_API_KEY
    if not key: raise Exception("Twelve Data API Key is missing.")
    url = f"https://api.twelvedata.com/exchange_rate?symbol={symbol}&apikey={key}"
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Exchange Rate Error: {response.status_code}")
    return response.json()

def get_twelve_data_currency_conversion(symbol: str, amount: float, api_key: str = None) -> dict:
    key = api_key or TWELVE_DATA_API_KEY
    if not key: raise Exception("Twelve Data API Key is missing.")
    url = f"https://api.twelvedata.com/currency_conversion?symbol={symbol}&amount={amount}&apikey={key}"
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"Conversion Error: {response.status_code}")
    return response.json()

def fetch_energy_price_api(symbol: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or ENERGY_PRICE_API_KEY
    if not key: raise Exception("EnergypriceAPI Key is missing.")
    
    url = f"https://api.energypriceapi.com/v1/timeframe?api_key={key}&start_date={start_date}&end_date={end_date}&base=USD&currencies={symbol}"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"EnergypriceAPI HTTP Error: {response.status_code}")
    
    res_json = response.json()
    if not res_json.get('success'):
        error_info = res_json.get('error', {}).get('info', 'Unknown error')
        raise Exception(f"EnergypriceAPI API Error: {error_info}")
        
    rates = res_json.get('rates', {})
    if not rates: raise Exception(f"No rates found for {symbol} in the given timeframe.")
    
    data_list = []
    for date_str, symbol_rates in rates.items():
        rate_val = symbol_rates.get(symbol)
        if rate_val and rate_val > 0:
            price_usd = 1.0 / rate_val
            data_list.append({
                "timestamp": date_str, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
            
    if not data_list: raise Exception(f"No valid price points for {symbol}")
    
    df = pd.DataFrame(data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{symbol}_EnergyPrice", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_metal_price_api(symbol: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or METAL_PRICE_API_KEY
    if not key: raise Exception("MetalpriceAPI Key is missing.")
    
    url = f"https://api.metalpriceapi.com/v1/timeframe?api_key={key}&start_date={start_date}&end_date={end_date}&base=USD&currencies={symbol}"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"MetalpriceAPI HTTP Error: {response.status_code}")
    
    res_json = response.json()
    if not res_json.get('success'):
        error_info = res_json.get('error', {}).get('info', 'Unknown error')
        raise Exception(f"MetalpriceAPI API Error: {error_info}")
        
    rates = res_json.get('rates', {})
    if not rates: raise Exception(f"No rates found for {symbol} in the given timeframe.")
    
    data_list = []
    for date_str, symbol_rates in rates.items():
        rate_val = symbol_rates.get(symbol)
        if rate_val and rate_val > 0:
            price_usd = 1.0 / rate_val
            data_list.append({
                "timestamp": date_str, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
            
    if not data_list: raise Exception(f"No valid price points for {symbol}")
    
    df = pd.DataFrame(data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{symbol}_MetalPrice", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_forex_rate_api(symbol: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or FOREX_RATE_API_KEY
    if not key: raise Exception("ForexRateAPI Key is missing.")
    
    url = f"https://api.forexrateapi.com/v1/timeframe?api_key={key}&start_date={start_date}&end_date={end_date}&base=USD&currencies={symbol}"
    
    response = requests.get(url)
    if response.status_code != 200: raise Exception(f"ForexRateAPI HTTP Error: {response.status_code}")
    
    res_json = response.json()
    if not res_json.get('success'):
        error_info = res_json.get('error', {}).get('info', 'Unknown error')
        raise Exception(f"ForexRateAPI API Error: {error_info}")
        
    rates = res_json.get('rates', {})
    if not rates: raise Exception(f"No rates found for {symbol} in the given timeframe.")
    
    data_list = []
    for date_str, symbol_rates in rates.items():
        rate_val = symbol_rates.get(symbol)
        if rate_val and rate_val > 0:
            price_usd = 1.0 / rate_val
            data_list.append({
                "timestamp": date_str, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
            
    if not data_list: raise Exception(f"No valid price points for {symbol}")
    
    df = pd.DataFrame(data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{symbol}_ForexRate", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_eia(dataset_info: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    # Reload config to pick up new keys dynamically
    config = _load_config()
    key = api_key or os.getenv("EIA_API_KEY", config.get("EIA_API_KEY", ""))
    
    if not key: 
        raise Exception("EIA API Key is missing. Please add it to config/api_keys.json as 'EIA_API_KEY'")
    
    # Handle ticker format "route:column" (e.g. "electricity/retail-sales:price")
    if ":" in dataset_info:
        dataset, data_col = dataset_info.split(":")
    else:
        dataset = dataset_info
        data_col = "quantity" # Fallback

    # Map interval to EIA frequency
    freq = "annual"
    try:
        delta = pd.to_datetime(end_date) - pd.to_datetime(start_date)
        if delta.days < 730:
            freq = "monthly"
    except:
        pass
        
    # EIA v2 Date Formatting: 
    # Annual: YYYY, Monthly: YYYY-MM
    if freq == "annual":
        start_val = start_date.split('-')[0]
        end_val = end_date.split('-')[0]
    else:
        start_val = start_date[:7] # YYYY-MM
        end_val = end_date[:7] # YYYY-MM
    
    url = f"https://api.eia.gov/v2/{dataset}/data/?frequency={freq}&data[0]={data_col}&start={start_val}&end={end_val}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={key}"
    
    response = requests.get(url)
    if response.status_code == 403:
        raise Exception("EIA API: 403 Forbidden. Your API Key might be invalid or restricted.")
    if response.status_code != 200:
        error_msg = response.json().get('error', {}).get('message', f"HTTP {response.status_code}")
        raise Exception(f"EIA API Error: {error_msg}")
    
    json_data = response.json()
    records = json_data.get('response', {}).get('data', [])
    if not records: raise Exception(f"No records found for EIA dataset: {dataset}")
    
    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['period'])
    # EIA returns values as strings in latest versions
    df['close'] = pd.to_numeric(df[data_col], errors='coerce')
    df.dropna(subset=['close'], inplace=True)
    
    # Aggregate to ensure unique timestamps (EIA data is often faceted)
    agg_df = df.groupby('timestamp')['close'].sum().reset_index()
    agg_df['open'] = agg_df['close']
    agg_df['high'] = agg_df['close']
    agg_df['low'] = agg_df['close']
    agg_df['volume'] = 0
    agg_df.sort_values('timestamp', inplace=True)
    
    series = _normalise_df(agg_df)
    return UploadResponse(filename=f"{dataset.replace('/', '_')}_EIA", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_external_stock_data(api_choice: str, ticker: str, start_date: str, end_date: str, api_key: Optional[str] = None) -> UploadResponse:
    # Resolve ticker name from the specific API's list
    # e.g., if api_choice is 'EnergypriceAPI' and ticker is 'Brent Crude Oil', resolve to 'BRENT'
    provider_tickers = _TICKER_MAP.get(api_choice, [])
    if isinstance(provider_tickers, list):
        for item in provider_tickers:
            if item.get("label") == ticker or item.get("value") == ticker:
                ticker = item.get("value")
                break
    
    api_choice = api_choice.lower()
    if "alpha vantage" in api_choice:
        return fetch_alpha_vantage(ticker, start_date, end_date, api_key)
    elif "financial prep" in api_choice or "fmp" in api_choice:
        return fetch_fmp(ticker, start_date, end_date, api_key)
    elif "polygon" in api_choice:
        return fetch_polygon(ticker, start_date, end_date, api_key)
    elif "twelve" in api_choice:
        return fetch_twelve_data(ticker, start_date, end_date, api_key)
    elif "eod" in api_choice:
        return fetch_eod(ticker, start_date, end_date, api_key)
    elif "ember" in api_choice:
        return fetch_ember(ticker, start_date, end_date, api_key)
    elif "energi" in api_choice:
        return fetch_energi_data_service(ticker, start_date, end_date)
    elif "energyprice" in api_choice:
        return fetch_energy_price_api(ticker, start_date, end_date, api_key)
    elif "metalprice" in api_choice:
        return fetch_metal_price_api(ticker, start_date, end_date, api_key)
    elif "forexrate" in api_choice:
        return fetch_forex_rate_api(ticker, start_date, end_date, api_key)
    elif "eia" in api_choice:
        return fetch_eia(ticker, start_date, end_date, api_key)
    else:
        raise ValueError(f"Unknown API choice: {api_choice}")
