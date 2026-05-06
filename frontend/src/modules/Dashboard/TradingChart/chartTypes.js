// ─── Chart Type Definitions ────────────────────────────────────────────────────
export const CHART_TYPES = [
  { id: 'candle_solid', label: 'Japanese Candlesticks', icon: '🕯️' },
  { id: 'area', label: 'Area Chart', icon: '📈' },
  { id: 'candle_stroke', label: 'Heikin Ashi', icon: '🔶' },
];


// ─── Technical Analysis: Indicators (overlay on main chart) ────────────────────
export const INDICATORS = [
  { id: 'MA',   label: 'SMA',                 category: 'trend' },
  { id: 'EMA',  label: 'EMA',                 category: 'trend' },
  { id: 'WMA',  label: 'WMA',                 category: 'trend' },
  { id: 'BOLL', label: 'Bollinger Bands',      category: 'volatility' },
  { id: 'SAR',  label: 'Parabolic SAR',        category: 'trend' },
  { id: 'SMA',  label: 'SMA (alt)',            category: 'trend' },
  { id: 'BBI',  label: 'BBI (Alligator-like)', category: 'trend' },
  // klinecharts built-in main indicators
];

// ─── Technical Analysis: Oscillators (sub-window pane) ─────────────────────────
export const OSCILLATORS = [
  { id: 'MACD', label: 'MACD' },
  { id: 'RSI',  label: 'RSI' },
  { id: 'KDJ',  label: 'Stochastic (KDJ)' },
  { id: 'CCI',  label: 'CCI' },
  { id: 'ATR',  label: 'Average True Range' },
  { id: 'AO',   label: 'Awesome Oscillator' },
  { id: 'MOM',  label: 'Momentum' },
  { id: 'ROC',  label: 'Rate Of Change' },
  { id: 'WR',   label: "Williams %R" },
  { id: 'DMI',  label: 'Average Directional Index' },
  { id: 'OBV',  label: 'OBV' },
  { id: 'VOL',  label: 'Volume' },
  { id: 'CR',   label: 'CR' },
  { id: 'VR',   label: 'VR' },
  { id: 'EMV',  label: 'EMV' },
  { id: 'MTM',  label: 'MTM' },
  { id: 'PSY',  label: 'PSY' },
  { id: 'TRIX', label: 'TRIX' },
];

// ─── Drawing Tools ─────────────────────────────────────────────────────────────
export const DRAWING_TOOLS = [
  { id: 'horizontalStraightLine', label: 'Horizontal Line',      icon: '─' },
  { id: 'verticalStraightLine',   label: 'Vertical Line',        icon: '│' },
  { id: 'straightLine',           label: 'Trend Line',           icon: '╱' },
  { id: 'rayLine',                label: 'Ray',                  icon: '→' },
  { id: 'fibonacciLine',          label: 'Fibonacci Levels',     icon: 'Fib' },
  { id: 'parallelStraightLine',   label: 'Parallel Channel',     icon: '═' },
  { id: 'priceLine',              label: 'Price Line',           icon: '$' },
];
