import React from "react";
import {
  Activity, TrendingUp, TrendingDown, Zap, Calendar, Clock,
  RotateCcw, Loader, Maximize2, CheckCircle, AlertTriangle
} from "lucide-react";
import ChartToolbar from "./TradingChart/ChartToolbar";
import { s } from "./DashboardStyles";
import { TIMEFRAMES, INTERVALS } from "./useDashboard";

export default function ChartView({
  mode, fileInfo, kpis, chartData, plotlyHtml, loadingChart,
  timeframe, interval, resampling, fullSeries, error,
  liveMode, setLiveMode,
  changeTimeframe, changeInterval,
  handleChartTypeChange, handleAddMainIndicator, handleAddSubIndicator,
  activeIndicators, activeOscillators, reset
}) {
  return (
    <>
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-title">
          <Activity size={24} color="var(--accent-primary)" />
          Market Overview
        </h2>
        <div style={s.pill} className="icon-pill" onClick={reset}>
          <RotateCcw size={14} /><span>Change Source</span>
        </div>
      </div>

      {/* Combined toolbar */}
      <div style={s.combinedBar}>
        {fileInfo && (
          <div style={s.fileTag}>
            <CheckCircle size={13} color="var(--success)" />
            <span>
              <strong style={{ color: "var(--text-primary)" }}>{fileInfo.name}</strong>
              {" · "}{fileInfo.size}{" · "}
              <strong>{fileInfo.rows.toLocaleString()}</strong> candles
            </span>
          </div>
        )}
        <div style={s.divider} />

        {/* Timeframe */}
        <div style={s.pillGroup}>
          <Calendar size={12} color="var(--text-secondary)" style={{ opacity: 0.55 }} />
          {TIMEFRAMES.map((tf) => (
            <div key={tf}
              className={`ctrl-pill${timeframe === tf ? " ctrl-pill-active" : ""}${resampling || !fullSeries.length ? " ctrl-pill-disabled" : ""}`}
              onClick={() => !resampling && fullSeries.length && changeTimeframe(tf)}
            >{tf}</div>
          ))}
          <div
            className={`ctrl-pill ctrl-pill-all${timeframe === "ALL" ? " ctrl-pill-active" : ""}${resampling || !fullSeries.length ? " ctrl-pill-disabled" : ""}`}
            onClick={() => !resampling && fullSeries.length && changeTimeframe("ALL")}
            title="Show all data"
          ><Maximize2 size={11} /></div>
        </div>

        <div style={s.divider} />

        {/* Interval */}
        <div style={s.pillGroup}>
          <Clock size={12} color="var(--text-secondary)" style={{ opacity: 0.55 }} />
          {INTERVALS.map((iv) => (
            <div key={iv}
              className={`ctrl-pill${interval === iv ? " ctrl-pill-active" : ""}${resampling || !fullSeries.length ? " ctrl-pill-disabled" : ""}`}
              onClick={() => !resampling && fullSeries.length && changeInterval(iv)}
            >{iv}</div>
          ))}
        </div>

        <div style={s.divider} />

        {resampling && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "var(--text-secondary)", fontSize: "0.78rem", marginLeft: "auto" }}>
            <Loader size={12} style={{ animation: "spin 0.8s linear infinite" }} /> Resampling…
          </div>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div style={{ ...s.errorBox, marginBottom: "1rem" }}>
          <AlertTriangle size={18} /><div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {kpis && (
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-label"><Zap size={16} /> Last Close</div>
            <div className="kpi-value">{kpis.current?.toFixed(2)}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Period Change</div>
            <div className={`kpi-value kpi-trend ${kpis.is_positive ? "positive" : "negative"}`}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              {kpis.is_positive ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
              {Math.abs(kpis.change_pct ?? 0).toFixed(2)}%
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Volatility</div>
            <div className="kpi-value">{kpis.volatility?.toFixed(2)}%</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Candles</div>
            <div className="kpi-value">{(kpis.points ?? chartData.length).toLocaleString()}</div>
          </div>

          {mode === "api" && (
            <div className="kpi-card" style={{ border: liveMode ? "1px solid var(--accent-primary)" : "1px solid var(--border-color)", background: liveMode ? "rgba(59,130,246,0.05)" : "" }}>
              <div className="kpi-label" style={{ color: liveMode ? "var(--accent-primary)" : "var(--text-secondary)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", justifyContent: "space-between", width: "100%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <Activity size={16} className={liveMode ? "pulse" : ""} /> Live Mode
                  </div>
                  <div onClick={() => setLiveMode(!liveMode)} style={{
                    width: "36px", height: "18px", borderRadius: "10px",
                    background: liveMode ? "var(--accent-primary)" : "var(--border-color)",
                    position: "relative", cursor: "pointer", transition: "0.3s"
                  }}>
                    <div style={{
                      width: "14px", height: "14px", borderRadius: "50%", background: "#fff",
                      position: "absolute", top: "2px", left: liveMode ? "20px" : "2px", transition: "0.3s"
                    }} />
                  </div>
                </div>
              </div>
              <div className="kpi-value" style={{ fontSize: "0.8rem", marginTop: "0.5rem", opacity: 0.8 }}>
                {liveMode ? "Refreshing every hour..." : "Manual Refresh Only"}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Plotly Chart */}
      <div className="dashboard-content" style={s.content}>
        <ChartToolbar
          onChartTypeChange={handleChartTypeChange}
          onAddMainIndicator={handleAddMainIndicator}
          onAddSubIndicator={handleAddSubIndicator}
          onStartDrawing={() => {}}
          onClearDrawings={() => {}}
          activeIndicators={activeIndicators}
          activeOscillators={activeOscillators}
        />

        {loadingChart && (
          <div style={s.chartOverlay}>
            <Loader className="spin" size={48} color="var(--accent-primary)" />
            <span style={{ marginTop: "1rem", color: "var(--text-secondary)" }}>Generating Plotly Chart...</span>
          </div>
        )}

        {plotlyHtml ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {Object.entries(plotlyHtml)
              .filter(([key]) => key !== 'forecast')
              .map(([key, html]) => (
                <div key={key} className="chart-window" style={{
                  borderRadius: '12px', overflow: 'hidden',
                  border: '1px solid var(--border-color)',
                  background: 'rgba(0,0,0,0.2)',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
                }}>
                  <iframe
                    srcDoc={html}
                    style={{ width: '100%', height: key === 'main' ? '500px' : '280px', border: 'none' }}
                    title={`Plotly ${key}`}
                  />
                </div>
              ))}
          </div>
        ) : (
          !loadingChart && <div style={s.emptyState}>No data to display. Fetch or upload data to see the chart.</div>
        )}
      </div>
    </>
  );
}
