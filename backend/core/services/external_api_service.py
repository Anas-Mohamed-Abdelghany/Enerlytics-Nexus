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
    return _load_ticker_map()

# Priority: Environment Var > JSON Config > Hardcoded Fallback
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", _CONFIG.get("ALPHA_VANTAGE_API_KEY", "05ZYZ70H6F5L9II9"))
FMP_API_KEY = os.getenv("FMP_API_KEY", _CONFIG.get("FMP_API_KEY", "bhZYEjY4PaWmDaM2I35GEInihiWq3Htf"))
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", _CONFIG.get("POLYGON_API_KEY", "0kurlMvit3vtYmKSSepicYws1zvpdkTY"))
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", _CONFIG.get("TWELVE_DATA_API_KEY", "ff69818c7b134877abcf08807de4367c"))
EOD_API_KEY = os.getenv("EOD_API_KEY", _CONFIG.get("EOD_API_KEY", "68457dd194b332.71068275"))
EMBER_API_KEY = os.getenv("EMBER_API_KEY", _CONFIG.get("EMBER_API_KEY", "ee854030-06e0-fae3-726a-0cfb7d66c08b"))
METAL_PRICE_API_KEY = os.getenv("METAL_PRICE_API_KEY", _CONFIG.get("METAL_PRICE_API_KEY", "8267fd1602aeb2a9f412fcf2729e4daa"))
FOREX_RATE_API_KEY = os.getenv("FOREX_RATE_API_KEY", _CONFIG.get("FOREX_RATE_API_KEY", "e39dc69cf0e81ca185b1b52732f76ad3"))
OIL_PRICE_API_KEY = os.getenv("OIL_PRICE_API_KEY", _CONFIG.get("OIL_PRICE_API_KEY", ""))
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

def fetch_ember(entity_code: str, start_date: str, end_date: str, interval: str = "1D", api_key: str = None) -> UploadResponse:
    key = api_key or EMBER_API_KEY
    if not key: raise Exception("Ember API Key is missing. Please add it to config/api_keys.json")
    
    # Map interval to Ember endpoint
    # Ember usually supports 'yearly' and 'monthly'
    endpoint = "yearly"
    if interval == "1M":
        endpoint = "monthly"
    
    # Dates: Yearly expects YYYY, Monthly expects YYYY-MM
    if endpoint == "yearly":
        start_val = start_date[:4]
        end_val = end_date[:4]
    else:
        start_val = start_date[:7]
        end_val = end_date[:7]
    
    url = f"https://api.ember-energy.org/v1/electricity-generation/{endpoint}?entity_code={entity_code}&start_date={start_val}&end_date={end_val}&api_key={key}"
    
    response = requests.get(url, timeout=25)
    if response.status_code != 200:
        raise Exception(f"Ember API Error: {response.status_code} - {response.text}")
        
    res_json = response.json()
    data = res_json.get('data', [])
    if not data:
        raise Exception(f"No Ember data found for {entity_code} in the specified range.")
        
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['date'])
    
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


def fetch_metal_price_api(symbol: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or METAL_PRICE_API_KEY
    if not key: raise Exception("MetalpriceAPI Key is missing.")
    
    # Some versions of MetalpriceAPI prefer 'currencies' over 'symbols'
    url = f"https://api.metalpriceapi.com/v1/timeframe?api_key={key}&start_date={start_date}&end_date={end_date}&base=USD&currencies={symbol}"
    
    response = requests.get(url, timeout=25)
    if response.status_code != 200: raise Exception(f"MetalpriceAPI HTTP Error: {response.status_code}")
    
    res_json = response.json()
    if not res_json.get('success'):
        error_obj = res_json.get('error', {})
        error_msg = error_obj.get('info') or error_obj.get('message') or res_json.get('message') or "Unknown error"
        raise Exception(f"MetalpriceAPI API Error: {error_msg}")
        
    rates = res_json.get('rates', [])
    if not rates: raise Exception(f"No rates found for {symbol} in the given timeframe.")
    
    data_list = []
    
    # MetalpriceAPI can return rates as a list or a dictionary
    if isinstance(rates, list):
        for item in rates:
            ts = item.get('timestamp') or item.get('date')
            symbol_rates = item.get('rates', {})
            
            # Prefer direct price (e.g. USDXAU) if available, otherwise use 1/XAU
            direct_key = f"USD{symbol}"
            if direct_key in symbol_rates:
                price_usd = float(symbol_rates[direct_key])
            elif symbol in symbol_rates and float(symbol_rates[symbol]) > 0:
                price_usd = 1.0 / float(symbol_rates[symbol])
            else:
                continue
                
            data_list.append({
                "timestamp": ts, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
    else:
        # Dict format: { "YYYY-MM-DD": { "XAU": ... } }
        for date_str, symbol_rates in rates.items():
            direct_key = f"USD{symbol}"
            if direct_key in symbol_rates:
                price_usd = float(symbol_rates[direct_key])
            elif symbol in symbol_rates and float(symbol_rates[symbol]) > 0:
                price_usd = 1.0 / float(symbol_rates[symbol])
            else:
                continue
                
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
    
    # The timeframe endpoint requires 'currency' for single currency requests
    url = f"https://api.forexrateapi.com/v1/timeframe?api_key={key}&start_date={start_date}&end_date={end_date}&base=USD&currency={symbol}"
    
    response = requests.get(url, timeout=25)
    if response.status_code != 200: raise Exception(f"ForexRateAPI HTTP Error: {response.status_code}")
    
    res_json = response.json()
    if not res_json.get('success'):
        error_obj = res_json.get('error', {})
        error_msg = error_obj.get('info') or error_obj.get('message') or res_json.get('message') or "Unknown error"
        raise Exception(f"ForexRateAPI API Error: {error_msg}")
        
    rates = res_json.get('rates', [])
    if not rates: raise Exception(f"No rates found for {symbol} in the given timeframe.")
    
    data_list = []
    
    # ForexRateAPI can return rates as a list or a dictionary
    if isinstance(rates, list):
        for item in rates:
            ts = item.get('timestamp') or item.get('date')
            symbol_rates = item.get('rates', {})
            
            # Prefer direct price (e.g. USDJPY) if available, otherwise use 1/JPY
            direct_key = f"USD{symbol}"
            if direct_key in symbol_rates:
                price_usd = float(symbol_rates[direct_key])
            elif symbol in symbol_rates and float(symbol_rates[symbol]) > 0:
                price_usd = 1.0 / float(symbol_rates[symbol])
            else:
                continue
                
            data_list.append({
                "timestamp": ts, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
    else:
        # Dict format: { "YYYY-MM-DD": { "JPY": ... } }
        for date_str, symbol_rates in rates.items():
            direct_key = f"USD{symbol}"
            if direct_key in symbol_rates:
                price_usd = float(symbol_rates[direct_key])
            elif symbol in symbol_rates and float(symbol_rates[symbol]) > 0:
                price_usd = 1.0 / float(symbol_rates[symbol])
            else:
                continue
                
            data_list.append({
                "timestamp": date_str, "open": price_usd, "high": price_usd, "low": price_usd, "close": price_usd, "volume": 0
            })
    
    if not data_list: raise Exception(f"No valid price points for {symbol}")
    
    df = pd.DataFrame(data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    series = _normalise_df(df)
    return UploadResponse(filename=f"{symbol}_ForexRate", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_oil_price_api(ticker: str, start_date: str, end_date: str, api_key: str = None) -> UploadResponse:
    key = api_key or OIL_PRICE_API_KEY
    if not key: raise Exception("Oil Price API Key is missing. Please add it to config/api_keys.json")
    
    # Use past_month for daily data within 30 days
    url = f"https://api.oilpriceapi.com/v1/prices/past_month?by_code={ticker}"
    
    headers = {"Authorization": f"Token {key}"}
    response = requests.get(url, headers=headers, timeout=25)
    
    if response.status_code != 200:
        raise Exception(f"Oil Price API Error: {response.status_code} - {response.text}")
        
    res_json = response.json()
    if res_json.get('status') != 'success':
        raise Exception(f"Oil Price API Error: {res_json.get('message', 'Unknown error')}")
        
    data = res_json.get('data')
    if not data:
        raise Exception(f"No Oil Price data found for {ticker}.")
        
    # If data is a dict containing a list (e.g. {'prices': [...]}), extract the list
    if isinstance(data, dict) and 'prices' in data:
        data = data['prices']
    elif isinstance(data, dict):
        data = [data] # Handle single object response (like /latest)
        
    df = pd.DataFrame(data)
    if df.empty:
        raise Exception(f"Oil Price API returned an empty data list for {ticker}.")
        
    # Find time column
    time_col = next((c for c in df.columns if c in ['created_at', 'date', 'timestamp', 'time']), None)
    if not time_col:
        raise Exception(f"Could not find a timestamp column in Oil Price API response. Columns: {list(df.columns)}")
        
    df['timestamp'] = pd.to_datetime(df[time_col], utc=True).dt.tz_localize(None)
    
    # Find price column
    price_col = next((c for c in df.columns if c in ['price', 'value', 'close']), None)
    if not price_col:
        raise Exception(f"Could not find a price column in Oil Price API response. Columns: {list(df.columns)}")
        
    df.rename(columns={price_col: 'close'}, inplace=True)
    df['open'] = df['close']
    df['high'] = df['close']
    df['low'] = df['close']
    df['volume'] = 0
    
    # Filter by user range
    filtered_df = df[(df['timestamp'] >= pd.to_datetime(start_date)) & (df['timestamp'] <= pd.to_datetime(end_date))]
    
    if not filtered_df.empty:
        df = filtered_df
    # Else: return everything the API gave us (fallback for 30-day trial limit)

    
    df.sort_values('timestamp', inplace=True)
    series = _normalise_df(df)
    return UploadResponse(filename=f"{ticker}_OilPrice", rows=len(series), series=series, kpis=_compute_kpis(series))

def fetch_eia(dataset_info: str, start_date: str, end_date: str, interval: str = "1D", api_key: str = None) -> UploadResponse:
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
    if interval == "1M":
        freq = "monthly"
    elif interval == "1W":
        freq = "weekly"
    elif interval == "1D":
        freq = "daily"
    else:
        # Fallback to auto-detection if unknown interval
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
    
    response = requests.get(url, timeout=25)
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

def fetch_external_stock_data(api_choice: str, ticker: str, start_date: str, end_date: str, interval: str = "1D", api_key: Optional[str] = None) -> UploadResponse:
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
        return fetch_ember(ticker, start_date, end_date, interval, api_key)
    elif "metalprice" in api_choice:
        return fetch_metal_price_api(ticker, start_date, end_date, api_key)
    elif "forexrate" in api_choice:
        return fetch_forex_rate_api(ticker, start_date, end_date, api_key)
    elif "eia" in api_choice:
        return fetch_eia(ticker, start_date, end_date, interval, api_key)
    elif "oil price" in api_choice.lower():
        return fetch_oil_price_api(ticker, start_date, end_date, api_key)
    else:
        raise ValueError(f"Unknown API choice: {api_choice}")
