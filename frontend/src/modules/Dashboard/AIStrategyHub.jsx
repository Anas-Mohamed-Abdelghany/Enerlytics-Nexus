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
  checkSamples, setCheckSamples,
  selectedStrategies, setSelectedStrategies,
  setShowStrategyInfo,
  showValidationDetails, setShowValidationDetails,
  showRobustnessDetails, setShowRobustnessDetails,
  handlePredict, handleStrategy, handleDownloadCSV
}) {
  return (
    <div style={s.strategySection}>
      <div style={s.sectionHeader}>
        <h3 style={s.sectionTitle}>AI Strategy &amp; Forecasting</h3>
      </div>

      {/* Settings Panel */}
      <div style={s.settingsPanel}>
        {/* Prediction Mode */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Prediction Mode</div>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {[{ value: "regression", label: "Price Regression" }, { value: "classification", label: "Directional Trend" }].map(opt => (
              <label key={opt.value} className="radio-chip" style={{ ...s.radioLabel, ...(predictionType === opt.value ? s.radioLabelActive : {}) }}>
                <input type="radio" name="predictionType" value={opt.value} checked={predictionType === opt.value}
                  onChange={(e) => setPredictionType(e.target.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(predictionType === opt.value ? s.radioTextActive : {}) }}>{opt.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div style={s.settingsDivider} />

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
              { value: "standard", label: "Standard LSTM" },
              { value: "bidirectional", label: "Bidirectional LSTM" },
              { value: "advanced", label: "LightGBM" },
              { value: "pretrained", label: "Pretrained Model" }
            ].map(opt => (
              <label key={opt.label} className="radio-chip" style={{ ...s.radioLabel, ...(architecture === opt.value ? s.radioLabelActive : {}) }}>
                <input type="radio" name="architecture" value={opt.value} checked={architecture === opt.value}
                  onChange={() => setArchitecture(opt.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(architecture === opt.value ? s.radioTextActive : {}) }}>{opt.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div style={s.settingsDivider} />

        {/* Robustness Samples */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Robustness Check Samples</div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {[5, 10, 15, 20].map(n => (
              <label key={n} className="radio-chip" style={{ ...s.radioLabel, ...(checkSamples === n ? s.radioLabelActive : {}) }}>
                <input type="radio" name="checkSamples" value={n} checked={checkSamples === n}
                  onChange={(e) => setCheckSamples(parseInt(e.target.value))} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(checkSamples === n ? s.radioTextActive : {}) }}>{n} Samples</span>
              </label>
            ))}
          </div>
        </div>

        <div style={s.settingsDivider} />

        {/* Strategy Selection */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Strategy Selection</div>
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
            {["Marubozu", "Price Action", "Range Trading", "Trend Trading", "Position Trading", "Day Trading", "Scalping", "Swing Trading", "Breakout Trading", "Retracement Trading", "Momentum Trading", "MACD Trading"].map(st => {
              const isActive = selectedStrategies.includes(st);
              return (
                <div key={st} className="radio-chip"
                  style={{ ...s.radioLabel, padding: "0.4rem 0.8rem", ...(isActive ? s.radioLabelActive : {}) }}
                  onClick={() => setSelectedStrategies(prev => prev.includes(st) ? prev.filter(x => x !== st) : [...prev, st])}
                >
                  <span style={{ ...s.radioText, fontSize: "0.78rem", ...(isActive ? s.radioTextActive : {}) }}>{st}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={s.strategyActionRow}>
        <div className={`modern-btn ${predicting || !fullSeries.length ? "ctrl-pill-disabled" : ""}`} onClick={handlePredict}>
          {predicting ? <Loader size={18} className="spin" /> : <Brain size={18} />}
          <span>Predict</span>
        </div>
        <div className={`modern-btn ${analyzing || !fullSeries.length || selectedStrategies.length === 0 ? "ctrl-pill-disabled" : ""}`}
          onClick={() => handleStrategy(selectedStrategies)}>
          {analyzing ? <Loader size={18} className="spin" /> : <Target size={18} />}
          <span>Execute Strategy</span>
        </div>
        <div className={`modern-btn ${analyzing || !fullSeries.length ? "ctrl-pill-disabled" : ""}`}
          onClick={() => handleStrategy()}
          style={{ background: "linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)", boxShadow: "0 10px 25px rgba(139, 92, 246, 0.3)" }}>
          <Zap size={18} /><span>Find Best</span>
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
