import React, { useState, useEffect, useMemo } from 'react';
import createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';
const Plot = createPlotlyComponent(Plotly);
import {
  Zap, Battery, TrendingUp, Sun, Play, Pause,
  RotateCcw, Download, Info, CheckCircle2, DollarSign,
  ArrowRight, LayoutGrid, Calendar, ArrowUpRight, ArrowDownRight,
  AlertTriangle, ChevronUp, ChevronDown, Target
} from 'lucide-react';

// ── Bloomberg-style Design Tokens ─────────────────────────────────────────────
const THEME = {
  bg: '#0d1018',
  panel: 'rgba(23, 27, 38, 0.7)',
  border: 'rgba(255, 255, 255, 0.08)',
  textPrimary: '#d8dff0',
  textSecondary: '#8a92a6',
  accent: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  solar: '#fbbf24',
  grid: '#6366f1',
  load: '#ff8c42'
};

const sparkLayout = {
  margin: { t: 0, b: 0, l: 0, r: 0 },
  xaxis: { visible: false },
  yaxis: { visible: false },
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  showlegend: false
};

const mainPlotLayout = {
  grid: { rows: 3, columns: 1, shared_xaxes: true, roworder: 'top to bottom' },
  margin: { t: 30, b: 40, l: 60, r: 20 },
  showlegend: true,
  legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: 1.1, font: { size: 10, color: THEME.textSecondary } },
  xaxis: { type: 'date', showgrid: false, zeroline: false, tickfont: { size: 10, color: THEME.textSecondary } },
  yaxis: { title: { text: 'Price (€/kWh)', font: { size: 10 } }, tickfont: { size: 9 }, gridcolor: 'rgba(255,255,255,0.05)', domain: [0.72, 1] },
  yaxis2: { title: { text: 'Power (kW)', font: { size: 10 } }, tickfont: { size: 9 }, gridcolor: 'rgba(255,255,255,0.05)', domain: [0.36, 0.64] },
  yaxis3: { title: { text: 'SOC (%)', font: { size: 10 } }, tickfont: { size: 9 }, gridcolor: 'rgba(255,255,255,0.05)', domain: [0, 0.28], range: [0, 105] },
  hovermode: 'x unified',
  template: 'plotly_dark',
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  shapes: [
    {
      type: 'line', xref: 'paper', yref: 'paper',
      x0: 0, x1: 1, y0: 0.68, y1: 0.68,
      line: { color: '#000', width: 2 }
    },
    {
      type: 'line', xref: 'paper', yref: 'paper',
      x0: 0, x1: 1, y0: 0.32, y1: 0.32,
      line: { color: '#000', width: 2 }
    }
  ]
};

// ── Components ────────────────────────────────────────────────────────────────

const KPICard = ({ title, value, icon, color, sparkData, trend }) => (
  <div className="bloomberg-card">
    <div className="card-header">
      <div className="title-area">
        <span className="card-title">{title}</span>
        <div className="card-value-row">
          <span className="card-value">{value}</span>
          {trend && (
            <span className={`trend ${trend > 0 ? 'up' : 'down'}`}>
              {trend > 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              {Math.abs(trend)}%
            </span>
          )}
        </div>
      </div>
      <div className="icon-wrap" style={{ color, background: `${color}15` }}>{icon}</div>
    </div>
    <div className="card-sparkline">
      <Plot
        data={[{
          y: sparkData || [],
          type: 'scatter',
          mode: 'lines',
          line: { color, width: 2, shape: 'spline' },
          fill: 'tozeroy',
          fillcolor: `${color}05`
        }]}
        layout={sparkLayout}
        style={{ width: '100%', height: '40px' }}
        config={{ displayModeBar: false, staticPlot: true }}
      />
    </div>
  </div>
);

const Skeleton = () => (
  <div className="skeleton-pulse" style={{ height: '100%', width: '100%', borderRadius: '12px' }} />
);

const AccuracyReport = ({ nrmse, mae, rmse, generalization }) => (
  <div className="main-panel accuracy-panel" style={{ borderLeft: `4px solid ${THEME.accent}`, width: '100%' }}>
    <div className="panel-header-row" style={{ marginBottom: '1.5rem' }}>
      <div className="panel-title-group">
        <TrendingUp size={18} color={THEME.accent} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Forecasting Accuracy & Model Validation</h3>
      </div>
      <div className="badge success" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
        Site 1 Accuracy: {(100 - nrmse).toFixed(2)}%
      </div>
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem' }}>
      <div className="accuracy-stat" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ fontSize: '0.75rem', color: THEME.textSecondary, textTransform: 'uppercase', letterSpacing: '0.05em' }}>NRMSE (Error Rate)</span>
        <span style={{ fontSize: '1.5rem', fontWeight: 800, color: THEME.accent }}>{nrmse.toFixed(2)}%</span>
      </div>
      <div className="accuracy-stat" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ fontSize: '0.75rem', color: THEME.textSecondary, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Mean Absolute Error</span>
        <span style={{ fontSize: '1.5rem', fontWeight: 800 }}>{mae.toFixed(2)} kW</span>
      </div>
      <div className="accuracy-stat" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ fontSize: '0.75rem', color: THEME.textSecondary, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Root Mean Square Error</span>
        <span style={{ fontSize: '1.5rem', fontWeight: 800 }}>{rmse.toFixed(2)} kW</span>
      </div>
      <div className="accuracy-stat" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ fontSize: '0.75rem', color: THEME.textSecondary, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Generalization Ratio</span>
        <span style={{ fontSize: '1.5rem', fontWeight: 800, color: generalization < 1.3 ? THEME.success : THEME.warning }}>{generalization.toFixed(2)}x</span>
      </div>
    </div>
    <div className="validation-footer" style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: `1px solid ${THEME.border}`, fontSize: '0.75rem', color: THEME.textSecondary, display: 'flex', alignItems: 'center', gap: '8px' }}>
      <Info size={14} />
      Audit Note: Validation performed on 2025 Test Window. Generalization score reflects zero-shot performance on unseen residential profiles.
    </div>
  </div>
);

// ── Main Dashboard Component ──────────────────────────────────────────────────

export default function BatteryDashboard({
  optimizerResult,
  forecastResult,
  priceHistory,
  historicalData,
  isLoading,
  timeframe,
  setTimeframe,
  interval,
  setInterval,
  architecture,
  aprilSource,
  septSource,
  predictionType,
  predictionHorizon,
  onManualOptimize
}) {
  const [replayStep, setReplayStep] = useState(0);
  const [isReplaying, setIsReplaying] = useState(false);
  const [auditData, setAuditData] = useState(null);
  const [isAuditing, setIsAuditing] = useState(false);
  const [expandedMonth, setExpandedMonth] = useState(null); // 'april' | 'september' | null

  const handleRunAudit = async () => {
    setIsAuditing(true);
    try {
      const resp = await fetch('http://localhost:8000/api/battery/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: historicalData,
          architecture: architecture,
          aprilSource: aprilSource,
          septSource: septSource,
          prediction_type: predictionType,
          horizon: predictionHorizon || timeframe
        })
      });
      const data = await resp.json();
      if (data.error) {
        alert(data.error);
        setIsAuditing(false);
        return;
      }
      setAuditData(data);
    } catch (e) {
      console.error("Audit failed", e);
    } finally {
      setIsAuditing(false);
    }
  };

  const handleDownloadAuditReport = () => {
    if (!auditData) return;

    const csvRows = [
      ["Enerlytics Official Audit Report - 2025 - FULL DATASET"],
      ["Generated Date", new Date().toLocaleString()],
      ["Model Architecture", "DirectMultiStep-LGBM-v2"],
      [],
      ["--- SUMMARY METRICS ---"],
      ["Period", "RMSE", "MAE/MAPE", "NRMSE", "Data Points"]
    ];

    Object.keys(auditData).forEach(key => {
      if (key !== 'overall_nrmse' && auditData[key].period) {
        const m = auditData[key];
        csvRows.push([m.period, m.rmse, m.mae, m.nrmse, m.points]);
      }
    });

    csvRows.push(["AGGREGATE PERFORMANCE", "", "", auditData.overall_nrmse + "%"]);
    csvRows.push([], ["--- DETAILED HOURLY AUDIT DATA ---"]);
    csvRows.push(["Period", "Timestamp", "load_p", "load_new", "pv_p", "selling_price_eur_kwh", "Delta (kW)", "MAE/MAPE", "RMSE", "NRMSE"]);

    Object.keys(auditData).forEach(month => {
      if (auditData[month].series) {
        auditData[month].series.forEach(p => {
          const absError = Math.abs(p.load_p - p.load_new);
          const sqError = Math.pow(p.load_p - p.load_new, 2);
          csvRows.push([
            auditData[month].period,
            p.ts,
            p.load_p,
            p.load_new,
            p.pv_p,
            p.selling_price_eur_kwh,
            p.delta,
            absError.toFixed(4),
            Math.sqrt(sqError).toFixed(4),
            p.error_pct + "%"
          ]);
        });
      }
    });



    const csvContent = csvRows.map(row => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Enerlytics_Official_Audit_Report_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  useEffect(() => {
    // Reset audit scorecard when a new prediction is triggered or settings change
    setAuditData(null);
  }, [forecastResult, architecture, predictionType]);

  useEffect(() => {
    let interval;
    if (isReplaying && optimizerResult?.timestamps) {
      interval = setInterval(() => {
        setReplayStep(prev => (prev + 1) % optimizerResult.timestamps.length);
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isReplaying, optimizerResult]);

  // Removed auto-trigger to allow manual start via button
  /*
  useEffect(() => {
    // Auto-trigger audit on mount if we have data and haven't run it yet
    if (!auditData && !isAuditing && historicalData?.length > 0) {
      handleRunAudit();
    }
  }, [historicalData]);
  */

  const stats = useMemo(() => {
    // Priority 1: Audit Data (if available)
    if (auditData?.april && auditData?.september) {
      const totalSavings = (auditData.april.optimization?.savings || 0) + (auditData.september.optimization?.savings || 0);
      const totalBase = (auditData.april.optimization?.baseline_bill || 0) + (auditData.september.optimization?.baseline_bill || 0);
      const avgScGain = ((auditData.april.optimization?.sc_gain_pct || 0) + (auditData.september.optimization?.sc_gain_pct || 0)) / 2;
      const avgNrmse = auditData.overall_nrmse || 0;

      return {
        savings: totalSavings,
        savings_pct: totalBase > 0 ? (totalSavings / totalBase * 100) : 0,
        sc_gain: avgScGain,
        soc: 50.0,
        grid: 0,
        solar: 0,
        baseline: totalBase,
        total: totalBase - totalSavings,
        nrmse: avgNrmse,
        isCompliant: (totalSavings / totalBase * 100) >= 15.0 && avgNrmse <= 15.0
      };
    }

    if (forecastResult?.is_audit && forecastResult.april && forecastResult.september) {
      const a_bill = (forecastResult.Annual_Bill_EUR?.['Baseline A'] || 0) + (forecastResult.Annual_Bill_EUR?.['Baseline B'] || 0);
      const ctrl_bill = (forecastResult.Annual_Bill_EUR?.['Your Controller'] || 0) * 2; // Approximate annual

      return {
        savings: (forecastResult["Savings vs. A (EUR)"]?.["Your Controller"] || 0),
        savings_pct: parseFloat(forecastResult["Savings vs. A (%)"]?.["Your Controller"]) || 0,
        soc: 50.0,
        grid: 0,
        solar: 0,
        baseline: (forecastResult["Annual Bill (EUR)"]?.["Baseline A"] || 0),
        total: (forecastResult["Annual Bill (EUR)"]?.["Your Controller"] || 0)
      };
    }

    if (!optimizerResult && historicalData?.length > 0) {
      // Find the last ACTUAL data point, skipping future forecast points
      const actuals = historicalData.filter(d => !d.is_forecast);
      const last = actuals.length > 0 ? actuals[actuals.length - 1] : (historicalData.length > 0 ? historicalData[0] : null);

      if (!last) return { savings: 0, savings_pct: 0, soc: 0, grid: 0, solar: 0, baseline: 0, total: 0 };

      return {
        savings: 0,
        savings_pct: 0,
        soc: (last.soc_reconstructed || 0) * 100,
        grid: last.grid_p || 0,
        solar: last.pv_p || 0,
        baseline: 0,
        total: 0
      };
    }
    if (!optimizerResult) return { savings: 0, savings_pct: 0, soc: 0, grid: 0, solar: 0, baseline: 0, total: 0 };

    const socLen = optimizerResult.soc_trajectory?.length || 0;
    const powerLen = optimizerResult.grid_import?.length || 0;

    // When not replaying, we show the 'Now' state (index 0)
    const currentStep = isReplaying ? replayStep : 0;
    const powerStep = Math.min(currentStep, powerLen > 0 ? powerLen - 1 : 0);

    return {
      savings: optimizerResult.savings_eur || 0,
      savings_pct: optimizerResult.savings_pct || 0,
      soc: (optimizerResult.soc_trajectory?.[currentStep] ?? 0) * 100,
      grid: optimizerResult.grid_import?.[powerStep] || 0,
      solar: forecastResult?.solar_forecast?.[powerStep] || 0,
      baseline: optimizerResult.baseline_cost_eur || 0,
      total: optimizerResult.total_cost_eur || 0
    };
  }, [optimizerResult, forecastResult, replayStep, isReplaying, historicalData]);



  const generateMainPlotData = () => {
    // Priority: Historical Data (Actuals) -> Optimizer Results (Simulated)
    if (historicalData?.length > 0) {
      const h = historicalData;
      const t = h.map(d => new Date(d.timestamp));

      return [
        {
          x: t, y: h.map(d => d.selling_price || d.close),
          type: 'bar', name: 'Actual Price (€/kWh)',
          marker: { color: h.map(d => (d.selling_price || d.close) > 0.1 ? THEME.danger : THEME.accent), opacity: 0.7 },
          xaxis: 'x', yaxis: 'y1'
        },
        {
          x: t, y: h.map(d => d.load_p),
          type: 'scatter', mode: 'lines', name: 'Actual Load',
          line: { color: THEME.load, width: 2 },
          xaxis: 'x', yaxis: 'y2'
        },
        {
          x: t, y: h.map(d => d.pv_p),
          type: 'scatter', mode: 'lines', name: 'Actual Solar PV',
          line: { color: THEME.solar, width: 2 },
          xaxis: 'x', yaxis: 'y2'
        },
        {
          x: t, y: h.map(d => d.grid_p),
          type: 'scatter', mode: 'lines', name: 'Actual Grid Import',
          line: { color: THEME.grid, width: 2, dash: 'dot' },
          xaxis: 'x', yaxis: 'y2'
        },
        {
          x: t, y: h.map(d => (d.soc_reconstructed || 0) * 100),
          type: 'scatter', mode: 'lines', name: 'Reconstructed SOC %',
          fill: 'tozeroy',
          fillcolor: 'rgba(16, 185, 129, 0.15)',
          line: { color: THEME.success, width: 3 },
          xaxis: 'x', yaxis: 'y3'
        },
        {
          x: t, y: h.map(d => d.battery_p),
          type: 'scatter', mode: 'lines', name: 'Actual Battery P',
          line: { color: THEME.accent, width: 2, dash: 'dash' },
          xaxis: 'x', yaxis: 'y2'
        },
        {
          x: t.filter((_, i) => h[i].battery_p < -0.1),
          y: h.filter(d => d.battery_p < -0.1).map(d => (d.soc_reconstructed || 0) * 100),
          mode: 'markers', name: 'Actual Charge',
          marker: { color: THEME.accent, size: 7, line: { width: 1, color: '#fff' } },
          xaxis: 'x', yaxis: 'y3'
        },
        {
          x: t.filter((_, i) => h[i].battery_p > 0.1),
          y: h.filter(d => d.battery_p > 0.1).map(d => (d.soc_reconstructed || 0) * 100),
          mode: 'markers', name: 'Actual Discharge',
          marker: { color: THEME.warning, size: 7, line: { width: 1, color: '#fff' } },
          xaxis: 'x', yaxis: 'y3'
        }
      ];
    }

    if (!optimizerResult) return [];
    const t = optimizerResult.timestamps;
    const limit = isReplaying ? replayStep + 1 : t.length;
    const currentT = t.slice(0, limit);

    return [
      // Panel 1: Price
      {
        x: t, y: priceHistory?.prices || [],
        type: 'bar', name: 'Price (€/kWh)',
        marker: { color: priceHistory?.prices?.map(p => p > 0.1 ? THEME.danger : THEME.accent), opacity: 0.7 },
        xaxis: 'x', yaxis: 'y1'
      },
      // Panel 2: Power
      {
        x: t, y: forecastResult?.load_forecast || [],
        type: 'scatter', mode: 'lines', name: 'Building Load',
        line: { color: THEME.load, width: 2 },
        xaxis: 'x', yaxis: 'y2'
      },
      {
        x: t, y: forecastResult?.solar_forecast || [],
        type: 'scatter', mode: 'lines', name: 'Solar PV',
        line: { color: THEME.solar, width: 2 },
        xaxis: 'x', yaxis: 'y2'
      },
      {
        x: currentT, y: optimizerResult.grid_import.slice(0, limit),
        type: 'scatter', mode: 'lines', name: 'Net Grid Flow',
        line: { color: THEME.grid, width: 2, dash: 'dot' },
        xaxis: 'x', yaxis: 'y2'
      },
      // Panel 3: SOC
      {
        x: currentT, y: optimizerResult.soc_trajectory.slice(0, limit).map(v => v * 100),
        type: 'scatter', mode: 'lines', name: 'Battery SOC %',
        fill: 'tozeroy',
        fillcolor: 'rgba(16, 185, 129, 0.15)',
        line: { color: THEME.success, width: 3 },
        xaxis: 'x', yaxis: 'y3'
      },
      {
        x: currentT.filter((_, i) => optimizerResult.charge_schedule[i] < -0.1),
        y: optimizerResult.soc_trajectory.slice(0, limit).filter((_, i) => optimizerResult.charge_schedule[i] < -0.1).map(v => v * 100),
        mode: 'markers', name: 'Charge Event',
        marker: { color: THEME.accent, size: 8, line: { width: 1, color: '#fff' } },
        xaxis: 'x', yaxis: 'y3'
      },
      {
        x: currentT.filter((_, i) => optimizerResult.discharge_schedule[i] > 0.1),
        y: optimizerResult.soc_trajectory.slice(0, limit).filter((_, i) => optimizerResult.discharge_schedule[i] > 0.1).map(v => v * 100),
        mode: 'markers', name: 'Discharge Event',
        marker: { color: THEME.warning, size: 8, line: { width: 1, color: '#fff' } },
        xaxis: 'x', yaxis: 'y3'
      }
    ];
  };

  const handleExport = () => {
    if (!optimizerResult) return;
    const csv = [
      "Timestamp,Action,SOC,Grid_kW,Price_EUR",
      ...optimizerResult.timestamps.map((t, i) => {
        const charge = optimizerResult.charge_schedule[i];
        const discharge = optimizerResult.discharge_schedule[i];
        const action = charge < -0.1 ? "CHARGE" : discharge > 0.1 ? "DISCHARGE" : "IDLE";
        return `${t},${action},${(optimizerResult.soc_trajectory[i] * 100).toFixed(1)},${optimizerResult.grid_import[i].toFixed(2)},${priceHistory?.prices?.[i] || 0}`;
      })
    ].join("\n");
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `BESS_Optimization_${new Date().toISOString()}.csv`;
    a.click();
  };

  const handleExportOptimizationLog = () => {
    const data = auditData || (forecastResult?.is_audit ? forecastResult : null);
    if (!data) return;

    let csvRows = [["Timestamp", "Action_P_Bat", "Action", "SoC", "Cost_EUR"]];

    ['april', 'september'].forEach(month => {
      if (data[month]?.optimization?.schedule) {
        data[month].optimization.schedule.forEach(row => {
          const action = row.action_p_bat < -0.1 ? "CHARGE" : row.action_p_bat > 0.1 ? "DISCHARGE" : "IDLE";
          csvRows.push([row.ts, row.action_p_bat, action, row.soc, row.cost_eur]);
        });
      }
    });

    const csvContent = csvRows.map(row => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `BESS_Optimization_Log_Audit_2025.csv`;
    link.click();
  };

  if (isLoading) {
    return (
      <div className="bloomberg-dashboard-skeleton">
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton-item" style={{ height: '140px' }}><Skeleton /></div>)}
        </div>
        <div className="skeleton-item" style={{ height: '600px', marginTop: '20px' }}><Skeleton /></div>
      </div>
    );
  }

  return (
    <div className="bloomberg-dashboard">

      {/* 2. Main Orchestration Chart */}
      <div className="main-panel chart-panel">
        <div className="panel-header-row">
          <div className="panel-title-group">
            <LayoutGrid size={18} color={THEME.accent} />
            <h3>Energy Management System Orchestration</h3>
          </div>
          <div className="panel-actions">
            <div className="control-group">
              <span className="group-label">View</span>
              <div className="timeframe-group">
                {['1W', '1M', '3M', '6M', '1Y', 'ALL'].map(tf => (
                  <button
                    key={tf}
                    className={`time-btn ${timeframe === tf ? 'active' : ''}`}
                    onClick={() => setTimeframe(tf)}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>

            <div className="control-group">
              <span className="group-label">Interval</span>
              <div className="timeframe-group">
                {['1H', '4H', '1D'].map(iv => (
                  <button
                    key={iv}
                    className={`time-btn ${interval === iv ? 'active' : ''}`}
                    onClick={() => setInterval(iv)}
                  >
                    {iv}
                  </button>
                ))}
              </div>
            </div>

            <div className="divider-v" />
            <button className="action-btn" onClick={() => setIsReplaying(!isReplaying)}>{isReplaying ? <Pause size={14} /> : <Play size={14} />} {isReplaying ? "Stop" : "Replay"}</button>
            <button className="action-btn" onClick={() => setReplayStep(0)}><RotateCcw size={14} /> Reset</button>
            <button className={`action-btn ${isAuditing ? 'loading' : ''}`} onClick={handleRunAudit} disabled={isAuditing}>
              <CheckCircle2 size={14} /> {isAuditing ? "Auditing..." : "Run Audit 2025"}
            </button>
            <button className="action-btn primary" onClick={handleExport}><Download size={14} /> Export</button>
          </div>
        </div>
        <Plot
          data={generateMainPlotData()}
          layout={mainPlotLayout}
          style={{ width: '100%', height: '600px' }}
          config={{ responsive: true, displayModeBar: false }}
        />
      </div>


      {/* 4. Price Heatmap */}
      <div className="main-panel heatmap-panel">
        <div className="panel-title-group"><Calendar size={18} color={THEME.accent} /><h3>Historical Price Pattern</h3></div>
        <Plot
          data={[{
            z: priceHistory?.hour_dow_matrix || Array(7).fill(0).map(() => Array(24).fill(0)),
            x: Array.from({ length: 24 }, (_, i) => i),
            y: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            type: 'heatmap', colorscale: 'Viridis', showscale: false
          }]}
          layout={{
            margin: { t: 30, b: 40, l: 40, r: 10 },
            xaxis: { title: 'Hour of Day', tickfont: { size: 9 }, color: THEME.textSecondary },
            yaxis: { tickfont: { size: 9 }, color: THEME.textSecondary },
            paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: THEME.textPrimary }
          }}
          style={{ width: '100%', height: '280px' }}
          config={{ displayModeBar: false }}
        />
      </div>

      {/* 3. Dynamic Audit Scorecard */}
      <div className="main-panel audit-panel" style={{ border: `2px solid ${THEME.solar}44`, background: `${THEME.solar}05`, marginBottom: '1.5rem', padding: '1.5rem' }}>
        <div className="panel-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div className="panel-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <TrendingUp size={24} color={THEME.solar} />
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: THEME.solar }}>
                  {auditData ? `Audit Summary: ${Object.keys(auditData).filter(k => auditData[k].period).map(k => auditData[k].period).join(' & ')}` : "High-Precision AI Performance Audit"}
                </h3>
                <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.6 }}>
                  {auditData ? "Validated performance metrics for the active data window." : "Validate energy forecasting accuracy and generate audit-ready reports for any selected timeframe."}
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {auditData && (
              <button className="action-btn" onClick={handleDownloadAuditReport} style={{ background: 'transparent', border: `1px solid ${THEME.solar}`, color: THEME.solar, padding: '0.5rem 1rem', borderRadius: '6px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Download size={14} /> Download Report
              </button>
            )}
            <button
              className={`action-btn ${isAuditing ? 'loading' : ''}`}
              onClick={handleRunAudit}
              disabled={isAuditing || !historicalData?.length}
              style={{ background: THEME.solar, color: THEME.bg, padding: '0.6rem 1.25rem', borderRadius: '6px', fontWeight: 600, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Zap size={16} /> {isAuditing ? "Auditing..." : (auditData ? "Re-run Accuracy Check" : "Run Accuracy Audit")}
            </button>
            {auditData && <span className="badge" style={{ background: THEME.solar, color: THEME.bg, padding: '0.4rem 0.8rem', borderRadius: '4px', fontWeight: 700 }}>NRMSE: {auditData.overall_nrmse}%</span>}
          </div>
        </div>

        {!auditData && !isAuditing && (
          <div style={{ textAlign: 'center', padding: '3rem', color: THEME.textSecondary }}>
            <Target size={40} opacity={0.2} style={{ marginBottom: '1rem', margin: '0 auto' }} />
            <p>Ready for Performance Validation.</p>
            <p style={{ fontSize: '0.8rem' }}>Click "Run Accuracy Audit" above to analyze the loaded dataset and generate detailed accuracy reports.</p>
          </div>
        )}

        {isAuditing && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="spin" style={{ width: '40px', height: '40px', border: '3px solid rgba(255,191,0,0.2)', borderTopColor: THEME.solar, borderRadius: '50%', margin: '0 auto 1rem' }} />
            <p style={{ color: THEME.solar, fontWeight: 600 }}>
              Crunching {
                (() => {
                  const activeTF = predictionHorizon || timeframe;
                  if (activeTF === 'Audit' || activeTF === 'ALL' || !historicalData) return historicalData?.length?.toLocaleString();
                  const map = { "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "Month 3 Audit": 31 };
                  const days = map[activeTF] || parseInt(activeTF) || 30;
                  return Math.min(historicalData.length, days * 96).toLocaleString();
                })()
              } data points...
            </p>
          </div>
        )}

        {auditData && (
          <>
            <div className="audit-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
              {Object.keys(auditData).filter(k => auditData[k].period).map(month => (
                <div key={month} className="audit-month-card" style={{ background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '12px', border: `1px solid ${THEME.border}` }}>
                  <h4 style={{ textTransform: 'uppercase', color: THEME.solar, marginBottom: '0.25rem' }}>{auditData[month].period} Window</h4>
                  <div style={{ fontSize: '0.7rem', color: THEME.solar, opacity: 0.7, marginBottom: '1rem', fontStyle: 'italic' }}>Engine: {auditData[month].source}</div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                    <div className="audit-stat">
                      <div style={{ fontSize: '0.7rem', color: THEME.textSecondary }}>RMSE (kW)</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800 }}>{auditData[month].rmse}</div>
                    </div>
                    <div className="audit-stat">
                      <div style={{ fontSize: '0.7rem', color: THEME.textSecondary }}>NRMSE (%)</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: THEME.solar }}>{auditData[month].nrmse}%</div>
                    </div>
                    <div className="audit-stat">
                      <div style={{ fontSize: '0.7rem', color: THEME.textSecondary }}>Savings (€)</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: THEME.success }}>€{auditData[month].optimization?.savings}</div>
                    </div>
                    <div className="audit-stat">
                      <div style={{ fontSize: '0.7rem', color: THEME.textSecondary }}>SC Gain</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: THEME.accent }}>+{auditData[month].optimization?.sc_gain_pct}%</div>
                    </div>
                  </div>
                  <button
                    className="action-btn"
                    style={{ width: '100%', marginTop: '1rem', background: 'rgba(255,255,255,0.05)', justifyContent: 'center' }}
                    onClick={() => setExpandedMonth(expandedMonth === month ? null : month)}
                  >
                    {expandedMonth === month ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    {expandedMonth === month ? "Hide Hourly Comparison" : "View Hourly Comparison"}
                  </button>
                </div>
              ))}
            </div>

            {expandedMonth && (
              <div className="audit-details-expanded" style={{ marginTop: '1.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: `1px solid ${THEME.border}`, overflow: 'hidden' }}>
                <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderBottom: `1px solid ${THEME.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600 }}>Hourly Audit Breakdown: {auditData[expandedMonth].period}</span>
                  <span style={{ fontSize: '0.75rem', color: THEME.textSecondary }}>Showing first 96 points (24h) for verification</span>
                </div>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead style={{ position: 'sticky', top: 0, background: '#1a1a1a', zIndex: 10 }}>
                      <tr style={{ textAlign: 'left', borderBottom: `1px solid ${THEME.border}` }}>
                        <th style={{ padding: '0.75rem' }}>Timestamp</th>
                        <th style={{ padding: '0.75rem' }}>load_p</th>
                        <th style={{ padding: '0.75rem' }}>load_new</th>
                        <th style={{ padding: '0.75rem' }}>Delta (kW)</th>
                        <th style={{ padding: '0.75rem' }}>Error %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(auditData[expandedMonth].series || []).slice(0, 96).map((item, i) => {
                        const actual = item.load_p;
                        const pred = item.load_new;
                        const delta = item.delta;
                        const err = item.error_pct;

                        return (
                          <tr key={i} style={{ borderBottom: `1px solid ${THEME.border}33`, opacity: 0.9 }}>
                            <td style={{ padding: '0.5rem 0.75rem', color: THEME.textSecondary }}>{new Date(item.ts).toLocaleString([], { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</td>
                            <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{actual}</td>
                            <td style={{ padding: '0.5rem 0.75rem', color: THEME.solar }}>{pred}</td>
                            <td style={{ padding: '0.5rem 0.75rem', color: delta > 0 ? THEME.danger : THEME.success }}>{delta > 0 ? '+' : ''}{delta}</td>
                            <td style={{ padding: '0.5rem 0.75rem' }}>{err}%</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* 4. Optimizer Action Table */}
      <div className="main-panel table-panel">
        <div className="panel-header-row">
          <div className="panel-title-group">
            <LayoutGrid size={18} color={THEME.accent} />
            <h3>BESS Operational Execution Schedule</h3>
          </div>
          <div className="panel-actions">
            {forecastResult?.is_audit && (
              <button
                className="action-btn"
                onClick={handleExportOptimizationLog}
                style={{ border: `1px solid ${THEME.success}`, color: THEME.success }}
              >
                <Download size={14} /> Save Result CSV (Audit Months)
              </button>
            )}
            {!forecastResult?.is_audit && forecastResult?.points && (
              <button
                className="action-btn"
                onClick={onManualOptimize}
                style={{ border: `1px solid ${THEME.solar}`, color: THEME.solar }}
              >
                <Zap size={14} /> Run Optimization
              </button>
            )}
            <button className="action-btn primary" onClick={onManualOptimize} style={{ background: THEME.solar, color: THEME.bg, border: 'none' }}>
              <Zap size={14} /> Calculate Battery Optimization
            </button>
          </div>
        </div>

        {/* Dynamic ROI Summary - shows manual optimizer or audit months */}
        {optimizerResult && (
          <div className="audit-bill-summary" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', marginBottom: '1.5rem', border: `1px solid ${THEME.border}` }}>
            <div>
              <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: THEME.success, marginBottom: '0.5rem' }}>Total Bill: {predictionHorizon || 'Current View'}</h4>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                  <div style={{ fontSize: '0.65rem', color: THEME.textSecondary }}>{(optimizerResult.total_cost_eur || 0) >= 0 ? 'Net Revenue (With Battery)' : 'Net Cost (With Battery)'}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: (optimizerResult.total_cost_eur || 0) >= 0 ? THEME.success : THEME.danger }}>{(optimizerResult.total_cost_eur || 0) < 0 ? '-' : ''}€{Math.abs(optimizerResult.total_cost_eur || 0).toFixed(2)}</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.65rem', color: THEME.textSecondary }}>Savings</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: THEME.success }}>€{Math.abs(optimizerResult.savings_eur || 0).toFixed(2)} ({Math.abs(optimizerResult.savings_pct || 0).toFixed(1)}%)</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.65rem', color: THEME.textSecondary }}>{(optimizerResult.baseline_cost_eur || 0) >= 0 ? 'Net Revenue (No Battery)' : 'Net Cost (No Battery)'}</div>
                  <div style={{ fontSize: '1rem', fontWeight: 600, color: (optimizerResult.baseline_cost_eur || 0) >= 0 ? THEME.success : THEME.danger }}>{(optimizerResult.baseline_cost_eur || 0) < 0 ? '-' : ''}€{Math.abs(optimizerResult.baseline_cost_eur || 0).toFixed(2)}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {!optimizerResult && (auditData || forecastResult?.is_audit) && (
          <div className="audit-bill-summary" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', marginBottom: '1.5rem', border: `1px solid ${THEME.border}` }}>
            {['april', 'september'].map(month => {
              const data = auditData?.[month] || forecastResult?.[month];
              return (
                <div key={month} style={{ borderRight: month === 'april' ? `1px solid ${THEME.border}` : 'none', paddingRight: month === 'april' ? '1rem' : 0 }}>
                  <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: THEME.success, marginBottom: '0.5rem' }}>Total Bill: {month} 2025</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: THEME.textSecondary }}>{(data?.optimization?.optimized_bill || 0) >= 0 ? 'Net Revenue (With Battery)' : 'Net Cost (With Battery)'}</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 800, color: (data?.optimization?.optimized_bill || 0) >= 0 ? THEME.success : THEME.danger }}>{(data?.optimization?.optimized_bill || 0) < 0 ? '-' : ''}€{Math.abs(data?.optimization?.optimized_bill || 0).toFixed(2)}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.65rem', color: THEME.textSecondary }}>{(data?.optimization?.baseline_bill || 0) >= 0 ? 'Net Revenue (No Battery)' : 'Net Cost (No Battery)'}</div>
                      <div style={{ fontSize: '1rem', fontWeight: 600, color: (data?.optimization?.baseline_bill || 0) >= 0 ? THEME.success : THEME.danger }}>{(data?.optimization?.baseline_bill || 0) < 0 ? '-' : ''}€{Math.abs(data?.optimization?.baseline_bill || 0).toFixed(2)}</div>
                    </div>
                  </div>
                  <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: THEME.success, fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <TrendingUp size={12} /> Savings: €{data?.optimization?.savings || 0} ({data?.optimization?.savings_pct || 0}%)
                  </div>
                </div>
              )
            })}
          </div>
        )}

        <div className="table-wrapper">
          <table>
            <thead><tr><th>Time</th><th>Action</th><th>Power (kW)</th><th>Price (€)</th><th>End SOC</th><th>P&L</th></tr></thead>
            <tbody>
              {(() => {
                const auditKeys = auditData ? Object.keys(auditData).filter(k => auditData[k].period) : [];
                const defaultKey = auditKeys.length > 0 ? auditKeys[0] : 'april';
                const activeMonth = expandedMonth || defaultKey;
                const activeAuditData = auditData?.[activeMonth] || forecastResult?.[activeMonth];

                let rows = [];
                let isManual = false;
                if (optimizerResult && optimizerResult.charge_schedule) {
                  rows = optimizerResult.charge_schedule.slice(0, 96);
                  isManual = true;
                } else if (activeAuditData?.optimization?.schedule) {
                  rows = activeAuditData.optimization.schedule.slice(0, 96);
                } else if (activeAuditData?.optimization?.charge_schedule) {
                  rows = activeAuditData.optimization.charge_schedule.slice(0, 96);
                }

                return rows.map((_, i) => {
                  let t, charge, discharge, price, soc, pnl;

                  if (isManual) {
                    // Manual optimization: read everything by index from optimizerResult
                    t = optimizerResult.timestamps?.[i];
                    charge = optimizerResult.charge_schedule?.[i] || 0;
                    discharge = optimizerResult.discharge_schedule?.[i] || 0;
                    price = priceHistory?.prices?.[i] || 0;
                    soc = optimizerResult.soc_trajectory?.[i] || 0;
                    pnl = (optimizerResult.grid_import?.[i] || 0) * price * 0.25 * -1
                      + (optimizerResult.grid_export?.[i] || 0) * price * 0.8 * 0.25;
                  } else {
                    // Audit row from backend schedule
                    const data = rows[i];
                    const isScheduleRow = !!data?.ts;
                    t = isScheduleRow ? data.ts : activeAuditData?.timestamps?.[i];
                    charge = isScheduleRow ? (data.action_p_bat < 0 ? -data.action_p_bat : 0) : (activeAuditData?.optimization?.charge_schedule?.[i] || 0);
                    discharge = isScheduleRow ? (data.action_p_bat > 0 ? data.action_p_bat : 0) : (activeAuditData?.optimization?.discharge_schedule?.[i] || 0);
                    price = isScheduleRow ? (activeAuditData?.series?.[i]?.selling_price_eur_kwh || 0) : (activeAuditData?.prices?.[i] || 0);
                    soc = isScheduleRow ? data.soc : (activeAuditData?.optimization?.soc?.[i] || 0);
                    pnl = isScheduleRow ? data.cost_eur : ((discharge - charge) * price * 0.25);
                  }

                  if (!t) return null;

                  const action = charge > 0.05 ? "CHARGE" : discharge > 0.05 ? "DISCHARGE" : "IDLE";
                  const rowStyle = action === "CHARGE" ? 'row-charge' : action === "DISCHARGE" ? 'row-discharge' : 'row-idle';

                  return (
                    <tr key={i} className={rowStyle} style={{ opacity: isReplaying && i > replayStep ? 0.3 : 1 }}>
                      <td>{new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                      <td><span className={`badge ${action.toLowerCase()}`}>{action}</span></td>
                      <td className="mono">{(charge > discharge ? charge : discharge).toFixed(3)}</td>
                      <td className="mono">€{price.toFixed(3)}</td>
                      <td className="mono">{(soc * 100).toFixed(1)}%</td>
                      <td className={`mono pnl ${pnl >= 0 ? 'plus' : ''}`}>
                        {pnl.toFixed(4)}€
                      </td>
                    </tr>
                  );
                });
              })()}
            </tbody>
          </table>
        </div>
      </div>

      {/* KPI Results Row - Updated after optimization */}
      <div className="hero-row">
        <KPICard title="Savings Today" value={`€${stats.savings.toFixed(2)}`} icon={<DollarSign size={22} />} color={THEME.success} sparkData={optimizerResult?.soc_trajectory || []} trend={stats.savings_pct} />
        <KPICard title="Current SOC" value={`${stats.soc.toFixed(1)}%`} icon={<Battery size={22} />} color={stats.soc > 50 ? THEME.success : stats.soc > 20 ? THEME.warning : THEME.danger} sparkData={optimizerResult?.soc_trajectory || []} />
        <KPICard title="Grid Import Now" value={`${stats.grid.toFixed(2)} kW`} icon={<Zap size={22} />} color={THEME.accent} sparkData={optimizerResult?.grid_import || historicalData?.map(d => d.grid_p) || []} />
        <KPICard title="Solar Generation" value={`${stats.solar.toFixed(2)} kW`} icon={<Sun size={22} />} color={THEME.solar} sparkData={forecastResult?.solar_forecast || historicalData?.map(d => d.pv_p) || []} />

        <div className="bloomberg-card constraints-card" style={{ borderLeft: `4px solid ${THEME.accent}` }}>
          <div className="card-header" style={{ marginBottom: '0.5rem' }}>
            <span className="card-title" style={{ color: THEME.accent, fontWeight: 800 }}>SYSTEM LIMITS</span>
            <Info size={16} color={THEME.textSecondary} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ color: THEME.textSecondary }}>Capacity</span>
              <span style={{ color: THEME.textPrimary, fontWeight: 700 }}>16.0 kWh</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ color: THEME.textSecondary }}>Max Power</span>
              <span style={{ color: THEME.textPrimary, fontWeight: 700 }}>8.0 kW</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ color: THEME.textSecondary }}>Grid Limit</span>
              <span style={{ color: THEME.textPrimary, fontWeight: 700 }}>6.0 kW</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ color: THEME.textSecondary }}>Round-trip η</span>
              <span style={{ color: THEME.textPrimary, fontWeight: 700 }}>90%</span>
            </div>
          </div>
          <div style={{ marginTop: '0.75rem', padding: '0.4rem', background: 'rgba(255,255,255,0.03)', borderRadius: '4px', textAlign: 'center' }}>
            <span style={{ color: THEME.textSecondary, fontSize: '0.65rem' }}>Initial SoC: <strong style={{ color: THEME.success }}>50%</strong></span>
          </div>
        </div>
      </div>

      <style>{`
                .bloomberg-dashboard { 
                    display: flex; flex-direction: column; gap: 1.5rem; padding: 1.5rem; 
                    background: transparent; color: ${THEME.textPrimary}; font-family: 'Inter', sans-serif;
                    width: 100%; box-sizing: border-box;
                }
                .hero-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; }
                .control-group { display: flex; flex-direction: column; gap: 4px; }
                .group-label { font-size: 0.65rem; color: ${THEME.textSecondary}; text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; padding-left: 4px; }
                .bloomberg-card { 
                    background: var(--bg-panel); border: 1px solid var(--border-color); 
                    border-radius: 14px; padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem;
                }
                .card-header { display: flex; justify-content: space-between; align-items: flex-start; }
                .card-title { font-size: 0.75rem; color: ${THEME.textSecondary}; text-transform: uppercase; letter-spacing: 0.05em; }
                .card-value-row { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.25rem; }
                .card-value { font-size: 1.75rem; font-weight: 800; }
                .trend { display: flex; align-items: center; gap: 2px; font-size: 0.75rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
                .trend.up { color: ${THEME.success}; background: rgba(16, 185, 129, 0.1); }
                .trend.down { color: ${THEME.danger}; background: rgba(239, 68, 68, 0.1); }
                .icon-wrap { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }

                .main-panel { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 20px; padding: 1.5rem; }
                .panel-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
                .panel-title-group { display: flex; align-items: center; gap: 0.75rem; }
                .panel-title-group h3 { font-size: 1.1rem; font-weight: 700; margin: 0; }
                .panel-actions { display: flex; gap: 0.6rem; }
                .action-btn { 
                    background: rgba(255,255,255,0.05); border: 1px solid ${THEME.border}; color: ${THEME.textPrimary};
                    padding: 0.5rem 0.9rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600; 
                    cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: 0.2s;
                }
                .action-btn:hover { background: rgba(255,255,255,0.1); }
                .action-btn.primary { background: ${THEME.success}; color: #fff; border: none; }

                .timeframe-group { display: flex; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 2px; border: 1px solid ${THEME.border}; }
                .time-btn { 
                    background: transparent; border: none; color: ${THEME.textSecondary}; 
                    padding: 0.4rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;
                    cursor: pointer; transition: 0.2s;
                }
                .time-btn:hover { color: ${THEME.textPrimary}; background: rgba(255,255,255,0.05); }
                .time-btn.active { background: ${THEME.accent}; color: #fff; }
                .divider-v { width: 1px; height: 24px; background: ${THEME.border}; margin: 0 0.5rem; align-self: center; }

                .alert-panel { border-color: ${THEME.danger}44; background: linear-gradient(180deg, ${THEME.danger}08 0%, var(--bg-panel) 100%); }
                .anomaly-list { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem; }
                .anomaly-item { display: flex; align-items: flex-start; gap: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid ${THEME.danger}; }
                .anomaly-ts { font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: ${THEME.textSecondary}; min-width: 80px; }
                .anomaly-flags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
                .flag-pill { font-size: 0.65rem; background: ${THEME.danger}22; color: ${THEME.danger}; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
                .integrity-note { font-size: 0.7rem; color: ${THEME.textSecondary}; font-style: italic; margin-top: 1rem; border-top: 1px solid ${THEME.border}; padding-top: 0.5rem; }
                .badge { font-size: 0.7rem; padding: 0.25rem 0.6rem; border-radius: 20px; font-weight: 700; }
                .badge.danger { background: ${THEME.danger}22; color: ${THEME.danger}; }

                .dual-row { display: flex; flex-direction: column; gap: 1.5rem; }
                .roi-content { display: flex; flex-direction: column; gap: 1.25rem; margin-top: 1.5rem; }
                .comparison-row { display: flex; align-items: center; justify-content: space-between; }
                .metric { display: flex; flex-direction: column; gap: 4px; }
                .metric .label { font-size: 0.8rem; color: ${THEME.textSecondary}; }
                .metric .val { font-size: 1.5rem; font-weight: 800; }
                .progress-bar-wrap { height: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; overflow: hidden; }
                .progress-fill { height: 100%; background: linear-gradient(90deg, ${THEME.accent}, ${THEME.success}); border-radius: 5px; }
                .savings-callout { 
                    display: flex; align-items: center; gap: 1rem; padding: 1rem; 
                    background: rgba(16, 185, 129, 0.08); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2);
                }
                .main-save { margin: 0; font-size: 1.05rem; }
                .sub-save { margin: 0; font-size: 0.85rem; color: ${THEME.textSecondary}; }
                .annual-projection { font-size: 0.85rem; color: ${THEME.textSecondary}; font-style: italic; display: flex; align-items: center; gap: 6px; }

                .table-wrapper { margin-top: 1.5rem; max-height: 400px; overflow-y: auto; }
                table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
                th { text-align: left; padding: 12px; color: ${THEME.textSecondary}; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid ${THEME.border}; }
                td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.03); }
                .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
                .badge { padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; }
                .badge.charge { color: ${THEME.accent}; background: rgba(59, 130, 246, 0.1); }
                .badge.discharge { color: ${THEME.success}; background: rgba(16, 185, 129, 0.1); }
                .badge.idle { color: ${THEME.textSecondary}; background: rgba(128,128,128,0.1); }
                .row-charge { background: rgba(59, 130, 246, 0.02); }
                .row-discharge { background: rgba(16, 185, 129, 0.02); }
                .pnl { font-weight: 600; }
                .pnl.plus { color: ${THEME.success}; }

                .skeleton-pulse { 
                    background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.03) 75%);
                    background-size: 200% 100%; animation: pulse 1.5s infinite;
                }
                @keyframes pulse { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

                ::-webkit-scrollbar { width: 6px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

                @media (min-width: 1200px) {
                  .dual-row { flex-direction: row; align-items: stretch; }
                  .dual-row > div { flex: 1; }
                }
            `}</style>
    </div>
  );
}
