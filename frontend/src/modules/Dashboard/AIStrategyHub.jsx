import React from "react";
import {
  Activity, TrendingUp, TrendingDown, Zap, Calendar, Clock,
  RotateCcw, Maximize2, Brain, Target, Info, ChevronDown, ChevronUp, Loader,
  Download
} from "lucide-react";
import SHAPWaterfall from "./SHAPWaterfall";
import HorizonSensitivityChart from "./HorizonSensitivityChart";
import { s } from "./DashboardStyles";

export default function AIStrategyHub({
  fullSeries, chartData, predicting, analyzing,
  predictionResult, statusMessage,
  predictionType, setPredictionType,
  predictionHorizon, setPredictionHorizon,
  trainingWindow, setTrainingWindow,
  architecture, setArchitecture,
  aprilSource, setAprilSource,
  septSource, setSeptSource,
  checkSamples, setCheckSamples,
  selectedStrategies, setSelectedStrategies,
  setShowStrategyInfo,
  showValidationDetails, setShowValidationDetails,
  showRobustnessDetails, setShowRobustnessDetails,
  handlePredict, handleStrategy, handleTrainAll, handleDownloadCSV
}) {
  return (
    <div style={s.strategySection}>
      <div style={s.sectionHeader}>
        <h3 style={s.sectionTitle}>AI Strategy &amp; Forecasting</h3>
      </div>

      {/* Settings Panel */}
      <div style={s.settingsPanel}>
        {/* Prediction Horizon */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Prediction Interval</div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {[3, 7, 14, 30, 90, "Audit"].map(h => (
              <label key={h} className="radio-chip" style={{ ...s.radioLabel, ...(predictionHorizon === h ? s.radioLabelActive : {}) }}>
                <input type="radio" name="predictionHorizon" value={h} checked={predictionHorizon === h}
                  onChange={(e) => setPredictionHorizon(e.target.value === "Audit" ? "Audit" : parseInt(e.target.value))} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(predictionHorizon === h ? s.radioTextActive : {}) }}>
                  {h === 3 ? "3 Days" : h === 7 ? "7 Days" : h === 14 ? "14 Days" : h === 30 ? "30 Days" : h === 90 ? "90 Days" : "Month 4 & 9 Audit"}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div style={s.settingsDivider} />

        {/* Training Window */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Training Data Window</div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {["1D", "3D", "1W", "2W", "1M", "3M", "6M", "1Y", "2Y", "3Y", "ALL"].map(w => (
              <label key={w} className="radio-chip" style={{ ...s.radioLabel, ...(trainingWindow === w ? s.radioLabelActive : {}) }}>
                <input type="radio" name="trainingWindow" value={w} checked={trainingWindow === w}
                  onChange={(e) => setTrainingWindow(e.target.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(trainingWindow === w ? s.radioTextActive : {}) }}>{w}</span>
              </label>
            ))}
          </div>
        </div>

        <div style={s.settingsDivider} />

        {/* Neural Architecture */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Neural Architecture</div>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {[
              { value: "lightgbm", label: "LightGBM" },
              { value: "advanced", label: "Advanced" },
              { value: "hybrid", label: "Hybrid" }
            ].map(opt => (
              <label key={opt.label} className="radio-chip" style={{ ...s.radioLabel, ...(architecture === opt.value ? s.radioLabelActive : {}) }}>
                <input type="radio" name="architecture" value={opt.value} checked={architecture === opt.value}
                  onChange={() => setArchitecture(opt.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(architecture === opt.value ? s.radioTextActive : {}) }}>{opt.label}</span>
              </label>
            ))}
          </div>
          
          {architecture === "hybrid" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem", padding: "1rem", background: "rgba(0,0,0,0.1)", borderRadius: "8px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>April Model Source</span>
                <select 
                  value={aprilSource} 
                  onChange={(e) => setAprilSource(e.target.value)}
                  style={{ padding: "0.5rem", borderRadius: "6px", background: "var(--bg-panel)", color: "var(--text-primary)", border: "1px solid var(--border-color)" }}
                >
                  <option value="lightgbm">LightGBM (Static)</option>
                  <option value="advanced">Advanced (Walk-Forward)</option>
                </select>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>September Model Source</span>
                <select 
                  value={septSource} 
                  onChange={(e) => setSeptSource(e.target.value)}
                  style={{ padding: "0.5rem", borderRadius: "6px", background: "var(--bg-panel)", color: "var(--text-primary)", border: "1px solid var(--border-color)" }}
                >
                  <option value="lightgbm">LightGBM (Static)</option>
                  <option value="advanced">Advanced (Walk-Forward)</option>
                </select>
              </div>
            </div>
          )}
        </div>


      </div>

      {/* Action Buttons */}
      <div style={{ ...s.strategyActionRow, flexDirection: "column", alignItems: "stretch", gap: "1rem" }}>

        <div className={`modern-btn ${predicting || !fullSeries.length ? "ctrl-pill-disabled" : ""}`}
          onClick={() => handleTrainAll("lightgbm")}
          style={{ background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)", boxShadow: "0 4px 12px rgba(99, 102, 241, 0.2)" }}>
          <Activity size={16} /><span>Train LightGBM</span>
        </div>

        <div style={s.settingsDivider} />


          <div className={`modern-btn ${predicting || !fullSeries.length ? "ctrl-pill-disabled" : ""}`} onClick={handlePredict}>
            {predicting ? <Loader size={18} className="spin" /> : <Brain size={18} />}
            <span>Predict</span>
          </div>

          {predictionResult && (
            <div className="modern-btn"
              onClick={() => {
                const combined = [...chartData, ...(predictionResult.forecast || [])];
                handleDownloadCSV(combined, "ai_strategy_prediction.csv");
              }}
              style={{
                background: "linear-gradient(135deg, #059669 0%, #047857 100%)",
                color: "#fff",
                border: "none",
                boxShadow: "0 10px 25px rgba(5, 150, 105, 0.3)"
              }}>
              <Download size={18} /><span>Save Prediction CSV</span>
            </div>
          )}
        </div>

        {/* Status */}
        {statusMessage && (
          <div style={s.statusArea}>
            {predicting || analyzing ? (
              <Loader size={14} className="spin" />
            ) : (
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#3b82f6", boxShadow: "0 0 10px #3b82f6" }} />
            )}
            <span style={s.statusText}>{statusMessage}</span>
          </div>
        )}
      </div>
      );
}
