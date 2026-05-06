// ─── Dark Theme for klinecharts ─────────────────────────────────────────────────
export function getDarkTheme() {
  return {
    grid: {
      show: true,
      horizontal: { show: true, size: 1, color: 'rgba(255,255,255,0.04)', style: 'dashed', dashValue: [4, 4] },
      vertical:   { show: false },
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#10b981', downColor: '#ef4444', noChangeColor: '#6b7280',
        upBorderColor: '#10b981', downBorderColor: '#ef4444', noChangeBorderColor: '#6b7280',
        upWickColor: '#10b981', downWickColor: '#ef4444', noChangeWickColor: '#6b7280',
      },
      area: {
        lineSize: 2, lineColor: '#3b82f6',
        value: 'close',
        backgroundColor: [{ offset: 0, color: 'rgba(59,130,246,0.25)' }, { offset: 1, color: 'rgba(59,130,246,0)' }],
      },
      priceMark: {
        show: true,
        high: { show: true, color: '#10b981', textColor: '#ffffff' },
        low:  { show: true, color: '#ef4444', textColor: '#ffffff' },
        last: { show: true, upColor: '#10b981', downColor: '#ef4444', noChangeColor: '#6b7280', line: { show: true, style: 'dashed' } },
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        text: { color: '#d4d4d8' },
      },
    },
    indicator: {
      ohlc: { upColor: 'rgba(16,185,129,0.7)', downColor: 'rgba(239,68,68,0.7)', noChangeColor: 'rgba(107,114,128,0.7)' },
      bars: [
        { style: 'fill', borderStyle: 'solid', borderSize: 1, borderDashedValue: [2, 2], upColor: 'rgba(16,185,129,0.7)', downColor: 'rgba(239,68,68,0.7)', noChangeColor: '#888888' },
      ],
      lines: [
        { size: 1, color: '#3b82f6', style: 'solid' },
        { size: 1, color: '#06b6d4', style: 'solid' },
        { size: 1, color: '#f59e0b', style: 'solid' },
        { size: 1, color: '#8b5cf6', style: 'solid' },
        { size: 1, color: '#ec4899', style: 'solid' },
      ],
      tooltip: { showRule: 'always', showType: 'standard', text: { color: '#d4d4d8' } },
    },
    xAxis: {
      show: true, size: 'auto',
      axisLine: { show: true, color: 'rgba(255,255,255,0.08)', size: 1 },
      tickText: { show: true, color: '#71717a', size: 11 },
      tickLine: { show: true, size: 1, color: 'rgba(255,255,255,0.08)' },
    },
    yAxis: {
      show: true, size: 'auto',
      axisLine: { show: false },
      tickText: { show: true, color: '#71717a', size: 11 },
      tickLine: { show: false },
    },
    separator: { size: 1, color: 'rgba(255,255,255,0.08)', fill: true, activeBackgroundColor: 'rgba(59,130,246,0.15)' },
    crosshair: {
      show: true,
      horizontal: {
        show: true,
        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: 'rgba(255,255,255,0.15)' },
        text: { show: true, color: '#ffffff', size: 11, borderColor: '#3b82f6', borderSize: 1, backgroundColor: '#3b82f6', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2, borderRadius: 2 },
      },
      vertical: {
        show: true,
        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: 'rgba(255,255,255,0.15)' },
        text: { show: true, color: '#ffffff', size: 11, borderColor: '#3b82f6', borderSize: 1, backgroundColor: '#3b82f6', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2, borderRadius: 2 },
      },
    },
    overlay: {
      point: { color: '#3b82f6', borderColor: '#ffffff', borderSize: 1, radius: 5, activeColor: '#06b6d4', activeBorderColor: '#ffffff', activeBorderSize: 1, activeRadius: 6 },
      line: { style: 'solid', color: '#3b82f6', size: 1, dashValue: [4, 2] },
      rect: { style: 'fill', color: 'rgba(59,130,246,0.15)', borderColor: '#3b82f6', borderSize: 1 },
      text: { color: '#d4d4d8', size: 12, borderColor: '#3b82f6', borderSize: 1, backgroundColor: 'rgba(59,130,246,0.15)', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2 },
    },
  };
}

// ─── Light Theme for klinecharts ────────────────────────────────────────────────
export function getLightTheme() {
  return {
    grid: {
      show: true,
      horizontal: { show: true, size: 1, color: 'rgba(0,0,0,0.04)', style: 'dashed', dashValue: [4, 4] },
      vertical: { show: false },
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#10b981', downColor: '#ef4444', noChangeColor: '#6b7280',
        upBorderColor: '#10b981', downBorderColor: '#ef4444', noChangeBorderColor: '#6b7280',
        upWickColor: '#10b981', downWickColor: '#ef4444', noChangeWickColor: '#6b7280',
      },
      area: {
        lineSize: 2, lineColor: '#2563eb',
        value: 'close',
        backgroundColor: [{ offset: 0, color: 'rgba(37,99,235,0.2)' }, { offset: 1, color: 'rgba(37,99,235,0)' }],
      },
      priceMark: {
        show: true,
        high: { show: true, color: '#10b981', textColor: '#0f172a' },
        low:  { show: true, color: '#ef4444', textColor: '#0f172a' },
        last: { show: true, upColor: '#10b981', downColor: '#ef4444', noChangeColor: '#6b7280', line: { show: true, style: 'dashed' } },
      },
      tooltip: { showRule: 'always', showType: 'standard', text: { color: '#334155' } },
    },
    indicator: {
      ohlc: { upColor: 'rgba(16,185,129,0.7)', downColor: 'rgba(239,68,68,0.7)', noChangeColor: 'rgba(107,114,128,0.7)' },
      bars: [
        { style: 'fill', borderStyle: 'solid', borderSize: 1, borderDashedValue: [2, 2], upColor: 'rgba(16,185,129,0.7)', downColor: 'rgba(239,68,68,0.7)', noChangeColor: '#888888' },
      ],
      lines: [
        { size: 1, color: '#2563eb', style: 'solid' },
        { size: 1, color: '#0891b2', style: 'solid' },
        { size: 1, color: '#d97706', style: 'solid' },
        { size: 1, color: '#7c3aed', style: 'solid' },
        { size: 1, color: '#db2777', style: 'solid' },
      ],
      tooltip: { showRule: 'always', showType: 'standard', text: { color: '#334155' } },
    },
    xAxis: {
      show: true, size: 'auto',
      axisLine: { show: true, color: 'rgba(0,0,0,0.08)', size: 1 },
      tickText: { show: true, color: '#64748b', size: 11 },
      tickLine: { show: true, size: 1, color: 'rgba(0,0,0,0.08)' },
    },
    yAxis: {
      show: true, size: 'auto',
      axisLine: { show: false },
      tickText: { show: true, color: '#64748b', size: 11 },
      tickLine: { show: false },
    },
    separator: { size: 1, color: 'rgba(0,0,0,0.08)', fill: true, activeBackgroundColor: 'rgba(37,99,235,0.1)' },
    crosshair: {
      show: true,
      horizontal: {
        show: true,
        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: 'rgba(0,0,0,0.12)' },
        text: { show: true, color: '#ffffff', size: 11, borderColor: '#2563eb', borderSize: 1, backgroundColor: '#2563eb', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2, borderRadius: 2 },
      },
      vertical: {
        show: true,
        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: 'rgba(0,0,0,0.12)' },
        text: { show: true, color: '#ffffff', size: 11, borderColor: '#2563eb', borderSize: 1, backgroundColor: '#2563eb', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2, borderRadius: 2 },
      },
    },
    overlay: {
      point: { color: '#2563eb', borderColor: '#0f172a', borderSize: 1, radius: 5, activeColor: '#0891b2', activeBorderColor: '#0f172a', activeBorderSize: 1, activeRadius: 6 },
      line: { style: 'solid', color: '#2563eb', size: 1, dashValue: [4, 2] },
      rect: { style: 'fill', color: 'rgba(37,99,235,0.1)', borderColor: '#2563eb', borderSize: 1 },
      text: { color: '#334155', size: 12, borderColor: '#2563eb', borderSize: 1, backgroundColor: 'rgba(37,99,235,0.1)', paddingLeft: 4, paddingRight: 4, paddingTop: 2, paddingBottom: 2 },
    },
  };
}
