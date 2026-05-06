const BASE_URL = "http://localhost:8000";

// ─── Generic helpers ──────────────────────────────────────────────────────────

async function _handleResponse(response, endpoint) {
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      const json = await response.json();
      detail = json.detail 
        ? (typeof json.detail === 'string' ? json.detail : JSON.stringify(json.detail))
        : JSON.stringify(json);
    } catch {
      detail = await response.text();
    }
    throw new Error(`${endpoint}: ${detail}`);
  }
  return response.json();
}

export async function get(endpoint, params = {}) {
  const url = new URL(BASE_URL + endpoint);
  Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v));

  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(url, { method: "GET", credentials: "include", signal: controller.signal });
    clearTimeout(tid);
    return _handleResponse(res, endpoint);
  } catch (e) {
    clearTimeout(tid);
    if (e.name === "AbortError") throw new Error(`${endpoint} timed out.`);
    throw e;
  }
}

export async function post(endpoint, body = {}) {
  const res = await fetch(BASE_URL + endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  return _handleResponse(res, endpoint);
}

// ─── Upload — multipart file POST ─────────────────────────────────────────────
export const uploadApi = {
  /**
   * Upload a raw file (CSV/TSV/JSON/XLSX/XLS) to the backend for parsing.
   * Returns UploadResponse: { filename, rows, series, kpis }
   */
  uploadFile: async (file) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/api/upload/`, {
      method: "POST",
      body: form,
      credentials: "include",
    });
    return _handleResponse(res, "/api/upload/");
  },
};

// ─── Resample ─────────────────────────────────────────────────────────────────
export const resampleApi = {
  /**
   * Filter + resample an existing OHLCV series server-side.
   * @param {Array}  series    - Full OHLCV series from uploadApi.uploadFile()
   * @param {string} timeframe - "1W" | "1M" | "3M" | "6M" | "1Y" | "ALL"
   * @param {string} interval  - "1min"|"5min"|"15min"|"30min"|"1H"|"4H"|"1D"|"1W"|"1M"
   * Returns ResampleResponse: { timeframe, interval, rows, series, kpis }
   */
  resample: (series, timeframe, interval) =>
    post("/api/resample/", { series, timeframe, interval }),
};

// ─── Market (External API Fetch) ─────────────────────────────────────────────
export const marketApi = {
  /**
   * Fetch from Alpha Vantage or Financial Prep
   * Returns same UploadResponse format as uploadFile.
   */
  fetchData: (api_choice, ticker, start_date, end_date) =>
    get("/api/market/fetch", { api_choice, ticker, start_date, end_date }),
  getTickers: () => 
    get("/api/market/tickers"),
};

// ─── Forecast (LSTM ML) ──────────────────────────────────────────────────────
export const forecastApi = {
  /**
   * Train an LSTM on the provided historical series and return predicted future points or classification.
   */
  fetchForecast: (market, horizonDays, series, predictionType = "regression", useBidirectional = true, checkSamples = 5) =>
    post("/api/forecast/", { 
      market, 
      horizon_days: horizonDays, 
      prediction_type: predictionType,
      use_bidirectional: useBidirectional,
      check_samples: checkSamples,
      series 
    }),
};

// ─── Strategy Analysis ────────────────────────────────────────────────────────
export const strategyApi = {
  analyze: (strategy, series) =>
    post("/api/strategy/analyze", { strategy, series }),
  
  getBest: (series) =>
    post("/api/strategy/best", { series }),
};

// ─── Chart (Plotly Backend) ───────────────────────────────────────────────────
export const chartApi = {
  /**
   * Request a Plotly HTML string from the backend for the given series.
   */
  renderChart: (series, ticker = "Market", theme = "dark", chart_type = "candlestick", indicators = null, vlines = null) =>
    post("/api/chart/render", { series, ticker, theme, chart_type, indicators, vlines }),
};

// ─── Utilities ────────────────────────────────────────────────────────────────
export const utilsApi = {
  getExchangeRate: (symbol) => 
    get("/api/utils/exchange-rate", { symbol }),
  
  convert: (symbol, amount) => 
    get("/api/utils/convert", { symbol, amount }),
};

