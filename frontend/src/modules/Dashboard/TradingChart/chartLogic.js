// ─── klinecharts v10 API helpers ─────────────────────────────────────────────
//
//  Breaking changes from v9 → v10:
//    - applyNewData()  → setDataLoader({ getBars }) + resetData()
//    - applyMoreData() → same DataLoader pattern
//    - removeIndicator(paneId, name) → removeIndicator({ name, paneId })
//
import { init, dispose } from 'klinecharts';
import { getDarkTheme, getLightTheme } from './chartThemes';

/**
 * Create a new klinecharts chart on the given DOM container.
 */
export function createChart(container, isDarkMode) {
  const chart = init(container);
  chart.setStyles(isDarkMode ? getDarkTheme() : getLightTheme());
  return chart;
}

/**
 * Load OHLCV data into the chart using the v10 DataLoader pattern.
 * Expects an array of { timestamp, open, high, low, close, volume }.
 */
export function loadData(chart, rawData) {
  if (!chart || !rawData || rawData.length === 0) return;

  // Normalise & sort ascending by timestamp
  const klineData = rawData
    .map((d) => {
      const price = d.price ?? 0;
      return {
        timestamp: new Date(d.timestamp ?? 0).getTime(),
        open:   d.open   ?? price,
        high:   d.high   ?? price,
        low:    d.low    ?? price,
        close:  d.close  ?? price,
        volume: d.volume ?? 0,
      };
    })
    .filter((d) => !isNaN(d.timestamp) && d.timestamp > 0)
    .sort((a, b) => a.timestamp - b.timestamp);

  // Use applyNewData to directly render the candles
  if (chart.applyNewData) {
    chart.applyNewData(klineData, false);
  } else {
    // Fallback for some v10 betas if applyNewData was renamed
    chart.setDataLoader({
      getBars: ({ callback }) => {
        callback(klineData, false);
      },
    });
    if (chart.resetData) chart.resetData();
  }
}

/**
 * Re-apply the correct theme (dark / light) to an existing chart.
 */
export function applyTheme(chart, isDarkMode) {
  if (!chart) return;
  chart.setStyles(isDarkMode ? getDarkTheme() : getLightTheme());
}

/**
 * Switch the candle render style.
 * Valid types: 'candle_solid' | 'candle_stroke' | 'ohlc' | 'area' | 'candle_up_stroke' | 'candle_down_stroke'
 */
export function setChartType(chart, type) {
  if (!chart) return;
  chart.setStyles({ candle: { type } });
}

/**
 * Add a main-pane overlay indicator (SMA, EMA, BOLL …).
 * isStack=true  → render on the candle pane itself.
 */
export function addMainIndicator(chart, name) {
  if (!chart) return;
  try {
    chart.createIndicator(name, true);
  } catch (e) {
    console.warn(`addMainIndicator(${name}):`, e.message);
  }
}

/**
 * Add a sub-pane indicator (oscillator: MACD, RSI …).
 * Returns the new pane ID so it can be removed later if needed.
 */
export function addSubIndicator(chart, name) {
  if (!chart) return null;
  try {
    return chart.createIndicator(name, false);
  } catch (e) {
    console.warn(`addSubIndicator(${name}):`, e.message);
    return null;
  }
}

/**
 * Remove a named indicator.
 * v10 signature: removeIndicator(filter?) where filter = { name, paneId? }
 */
export function removeIndicator(chart, name, paneId) {
  if (!chart) return;
  try {
    chart.removeIndicator(paneId ? { name, paneId } : { name });
  } catch (e) {
    console.warn(`removeIndicator(${name}):`, e.message);
  }
}

/**
 * Start drawing an overlay (trend line, Fibonacci, etc.).
 */
export function startDrawing(chart, overlayName) {
  if (!chart) return;
  try {
    chart.createOverlay(overlayName);
  } catch (e) {
    console.warn(`startDrawing(${overlayName}):`, e.message);
  }
}

/**
 * Remove ALL drawing overlays from the chart.
 * v10: removeOverlay() with no filter removes everything.
 */
export function clearAllDrawings(chart) {
  if (!chart) return;
  try {
    chart.removeOverlay();
  } catch (e) {
    console.warn('clearAllDrawings:', e.message);
  }
}

/**
 * Dispose of the chart instance and free its DOM resources.
 */
export function destroyChart(container) {
  try {
    dispose(container);
  } catch (e) {
    // already disposed — safe to ignore
  }
}
