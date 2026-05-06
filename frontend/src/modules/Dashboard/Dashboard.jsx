import React from "react";
import useDashboard from "./useDashboard";
import { s, css } from "./DashboardStyles";

// Sub-components
import SourceSelector from "./SourceSelector";
import ApiForm from "./ApiForm";
import UploadView from "./UploadView";
import ChartView from "./ChartView";
import AIStrategyHub from "./AIStrategyHub";
import StrategyInfoPage from "./StrategyInfoPage";
import Forecaster from "../Forecaster";

export default function Dashboard({ isDarkMode }) {
  // Pull all state and logic from our custom hook
  const dashboard = useDashboard(isDarkMode);

  const {
    mode, setMode, uploading, chartData,
    setShowHowItWorks, showStrategyInfo, setShowStrategyInfo,
    predictionResult, predicting, loadingChart, plotlyHtml,
  } = dashboard;

  // ── 1. Source selector (Landing) ──────────────────────────────────────────
  if (!mode) return (
    <SourceSelector setMode={setMode} setShowHowItWorks={setShowHowItWorks} />
  );

  // ── 2. API Fetch View ─────────────────────────────────────────────────────
  if (mode === "api" && !chartData.length && !uploading) return (
    <ApiForm {...dashboard} />
  );

  // ── 3. Upload View ────────────────────────────────────────────────────────
  if (mode === "upload" && !chartData.length && !uploading) return (
    <UploadView {...dashboard} />
  );

  // ── 4. Uploading Spinner ──────────────────────────────────────────────────
  if (uploading) return (
    <section className="glass-panel">
      <div style={{ height: "400px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1.5rem" }}>
        <div style={s.spinner} />
        <p style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>Uploading &amp; parsing on server…</p>
      </div>
      <style>{css}</style>
    </section>
  );

  // ── 5. Main Chart View & Strategy Hub ─────────────────────────────────────
  return (
    <section className="glass-panel">
      {/* Top Chart Area */}
      <ChartView {...dashboard} />

      {/* AI Strategy Settings & Actions */}
      <AIStrategyHub {...dashboard} />

      {/* Strategy Info Overlay (Full Screen) */}
      {showStrategyInfo && (
        <StrategyInfoPage setShowStrategyInfo={setShowStrategyInfo} />
      )}

      {/* AI Price Forecast Plot (from Forecaster.jsx) */}
      <div style={{ marginTop: "2rem" }}>
        <Forecaster
          plotlyHtml={plotlyHtml}
          predictionResult={predictionResult}
          isPredicting={predicting}
          isLoadingChart={loadingChart}
        />
      </div>

      <style>{css}</style>
    </section>
  );
}
