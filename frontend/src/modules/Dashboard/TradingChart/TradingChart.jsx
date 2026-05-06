import React, { useEffect, useRef, useState, useCallback } from 'react';
import ChartToolbar from './ChartToolbar';
import {
  createChart,
  loadData,
  applyTheme,
  setChartType,
  addMainIndicator,
  addSubIndicator,
  startDrawing,
  clearAllDrawings,
  destroyChart,
} from './chartLogic';

export default function TradingChart({ data, isDarkMode }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);

  const [activeIndicators, setActiveIndicators] = useState([]);
  const [activeOscillators, setActiveOscillators] = useState([]);

  // ── 1. Create chart on mount ──────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, isDarkMode);
    chartRef.current = chart;
    
    // Automatically apply API.py chart layout (MA50/200, BOLL, MACD, RSI)
    try {
      chart.createIndicator({ name: 'MA', calcParams: [50, 200] }, true, { id: 'candle_pane' });
      chart.createIndicator('BOLL', true, { id: 'candle_pane' });
      chart.createIndicator('MACD', false);
      chart.createIndicator('RSI', false);
      
      setActiveIndicators(['MA', 'BOLL']);
      setActiveOscillators(['MACD', 'RSI']);
    } catch (e) {
      console.warn("Error applying API.py layout:", e);
    }

    return () => {
      destroyChart(containerRef.current);
      chartRef.current = null;
    };
  }, []); // mount only

  // ── 2. Re-apply theme when mode changes ───────────────────────────────────
  useEffect(() => {
    applyTheme(chartRef.current, isDarkMode);
  }, [isDarkMode]);

  // ── 3. Load data whenever it changes ──────────────────────────────────────
  useEffect(() => {
    loadData(chartRef.current, data);
  }, [data]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleChartTypeChange = useCallback((type) => {
    setChartType(chartRef.current, type);
  }, []);

  const handleAddMainIndicator = useCallback((name) => {
    addMainIndicator(chartRef.current, name);
    setActiveIndicators(prev => [...prev, name]);
  }, []);

  const handleAddSubIndicator = useCallback((name) => {
    addSubIndicator(chartRef.current, name);
    setActiveOscillators(prev => [...prev, name]);
  }, []);

  const handleStartDrawing = useCallback((overlayName) => {
    startDrawing(chartRef.current, overlayName);
  }, []);

  const handleClearDrawings = useCallback(() => {
    clearAllDrawings(chartRef.current);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <ChartToolbar
        onChartTypeChange={handleChartTypeChange}
        onAddMainIndicator={handleAddMainIndicator}
        onAddSubIndicator={handleAddSubIndicator}
        onStartDrawing={handleStartDrawing}
        onClearDrawings={handleClearDrawings}
        activeIndicators={activeIndicators}
        activeOscillators={activeOscillators}
      />
      <div
        ref={containerRef}
        style={{ flex: 1, minHeight: 0, width: '100%' }}
      />
    </div>
  );
}
