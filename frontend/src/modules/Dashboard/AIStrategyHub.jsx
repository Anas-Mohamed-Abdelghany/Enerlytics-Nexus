import React from "react";
import {
  Activity, TrendingUp, TrendingDown, Zap, Calendar, Clock,
  RotateCcw, Maximize2, Brain, Target, Info, ChevronDown, ChevronUp, Loader
} from "lucide-react";
import { s } from "./DashboardStyles";

export default function AIStrategyHub({
  fullSeries, chartData, predicting, analyzing,
  predictionResult, statusMessage,
  predictionType, setPredictionType,
  predictionHorizon, setPredictionHorizon,
  trainingWindow, setTrainingWindow,
  useBidirectional, setUseBidirectional,
  checkSamples, setCheckSamples,
  selectedStrategies, setSelectedStrategies,
  setShowStrategyInfo,
  showValidationDetails, setShowValidationDetails,
  showRobustnessDetails, setShowRobustnessDetails,
  handlePredict, handleStrategy
}) {
  return (
    <div style={{ ...s.strategySection, marginTop: "2rem" }}>
      <div style={s.sectionHeader}>
        <Brain size={18} color="var(--accent-primary)" />
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
            {[3, 7, 14, 30, 90].map(h => (
              <label key={h} className="radio-chip" style={{ ...s.radioLabel, ...(predictionHorizon === h ? s.radioLabelActive : {}) }}>
                <input type="radio" name="predictionHorizon" value={h} checked={predictionHorizon === h}
                  onChange={(e) => setPredictionHorizon(parseInt(e.target.value))} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(predictionHorizon === h ? s.radioTextActive : {}) }}>
                  {h === 3 ? "3 Days" : h === 7 ? "7 Days" : h === 14 ? "14 Days" : h === 30 ? "30 Days" : "90 Days"}
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
            {["1M", "3M", "6M", "1Y", "2Y", "3Y", "ALL"].map(w => (
              <label key={w} className="radio-chip" style={{ ...s.radioLabel, ...(trainingWindow === w ? s.radioLabelActive : {}) }}>
                <input type="radio" name="trainingWindow" value={w} checked={trainingWindow === w}
                  onChange={(e) => setTrainingWindow(e.target.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(trainingWindow === w ? s.radioTextActive : {}) }}>{w}</span>
              </label>
            ))}
          </div>
          <p style={{ margin: 0, fontSize: "0.7rem", color: "rgba(0,0,0,0.5)", fontStyle: "italic" }}>
            *Logical Tip: Use a Training Window at least 5-10x longer than your Prediction Interval for optimal model stability.
          </p>
        </div>

        <div style={s.settingsDivider} />

        {/* Neural Architecture */}
        <div style={s.settingsGroup}>
          <div style={s.groupLabel}>Neural Architecture</div>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {[{ value: false, label: "Standard LSTM" }, { value: true, label: "Bidirectional LSTM" }].map(opt => (
              <label key={opt.label} className="radio-chip" style={{ ...s.radioLabel, ...(useBidirectional === opt.value ? s.radioLabelActive : {}) }}>
                <input type="radio" name="useBidirectional" value={opt.value} checked={useBidirectional === opt.value}
                  onChange={() => setUseBidirectional(opt.value)} style={s.radioHidden} />
                <span style={{ ...s.radioText, ...(useBidirectional === opt.value ? s.radioTextActive : {}) }}>{opt.label}</span>
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
          <div style={{ ...s.groupLabel, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            Manual Strategy Selection
            <div style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "0.3rem", color: "var(--accent-primary)", textTransform: "none", fontSize: "0.7rem" }} onClick={() => setShowStrategyInfo(true)}>
              <Info size={14} /> Strategy Details
            </div>
          </div>
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
      </div>

      {/* Status */}
      {statusMessage && (
        <div style={s.statusArea}>
          {predicting || analyzing ? (
            <Loader size={14} className="spin" />
          ) : (
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent-primary)", boxShadow: "0 0 10px var(--accent-primary)" }} />
          )}
          <span style={s.statusText}>{statusMessage}</span>
        </div>
      )}

      {/* XAI Feature Importance */}
      {predictionResult?.feature_importance && (
        <div className="glass-panel" style={{ marginTop: "1rem", padding: "1.5rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "#000" }}>
            <Brain size={20} color="#06b6d4" /> Explainable AI (XAI): Feature Importance
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {Object.entries(predictionResult.feature_importance).sort((a, b) => b[1] - a[1]).map(([key, val]) => (
              <div key={key} style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <div style={{ width: "120px", fontSize: "0.85rem", color: "#000" }}>{key.replace('_', ' ')}</div>
                <div style={{ flex: 1, height: "8px", background: "rgba(0,0,0,0.05)", borderRadius: "4px", overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${val * 100}%`, background: "#06b6d4", borderRadius: "4px" }} />
                </div>
                <div style={{ width: "40px", fontSize: "0.85rem", color: "#06b6d4", fontWeight: "600" }}>{(val * 100).toFixed(0)}%</div>
              </div>
            ))}
          </div>
          <p style={{ marginTop: "1rem", fontSize: "0.75rem", color: "rgba(0,0,0,0.5)", fontStyle: "italic" }}>
            *This chart shows which data factors most heavily influenced the neural network's current prediction.
          </p>
        </div>
      )}

      {/* Validation Report */}
      {predictionResult?.validation_details && (
        <ValidationReport
          details={predictionResult.validation_details.filter(d => d.type === 'VALIDATION')}
          show={showValidationDetails} setShow={setShowValidationDetails}
          title="AI Validation Integrity Report" subtitle="Hold-out Set (Latest 10% Unseen Data)"
          color="#06b6d4" lastColLabel="Integrity"
        />
      )}

      {/* Robustness Report */}
      {predictionResult?.validation_details && (
        <ValidationReport
          details={predictionResult.validation_details.filter(d => d.type === 'CHECK')}
          show={showRobustnessDetails} setShow={setShowRobustnessDetails}
          title="AI Robustness Check Report"
          subtitle={`Historical Random Segments (${checkSamples} Samples)`}
          color="#d97706" lastColLabel="Consistency"
          footnote="*This report validates model consistency by re-running analysis on random historical segments. Higher consistency scores indicate a model that has successfully generalized the market's behavior."
        />
      )}
    </div>
  );
}

// ── Shared validation/robustness table ────────────────────────────────────────
function ValidationReport({ details, show, setShow, title, subtitle, color, lastColLabel, footnote }) {
  return (
    <div className="glass-panel" style={{ marginTop: "1rem", padding: "1.5rem", background: "rgba(255,255,255,0.95)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: show ? "1.5rem" : "0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem", color: "#000" }}>
            <Activity size={20} color={color} /> {title}
          </h3>
          <div style={{ fontSize: "0.8rem", color, fontWeight: "600", padding: "0.3rem 0.6rem", background: `${color}0d`, borderRadius: "6px" }}>
            {subtitle}
          </div>
        </div>
        <div onClick={() => setShow(!show)} style={{
          cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem",
          color, fontWeight: "700", fontSize: "0.85rem", padding: "0.5rem 1rem",
          borderRadius: "10px", background: `${color}0d`, transition: "all 0.2s"
        }} className="hover-opacity">
          {show ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          <span>{show ? "Shrink Report" : "Expand Report"}</span>
        </div>
      </div>

      {show && (
        <div style={{ overflowX: "auto", marginTop: "1.5rem", animation: "fadeIn 0.3s ease-out" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", color: "#000" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid rgba(0,0,0,0.1)" }}>
                <th style={{ textAlign: "left", padding: "0.75rem", fontSize: "0.85rem", color: "rgba(0,0,0,0.5)" }}>Date</th>
                <th style={{ textAlign: "center", padding: "0.75rem", fontSize: "0.85rem", color: "rgba(0,0,0,0.5)" }}>Actual Outcome</th>
                <th style={{ textAlign: "center", padding: "0.75rem", fontSize: "0.85rem", color: "rgba(0,0,0,0.5)" }}>AI Prediction</th>
                <th style={{ textAlign: "right", padding: "0.75rem", fontSize: "0.85rem", color: "rgba(0,0,0,0.5)" }}>{lastColLabel}</th>
              </tr>
            </thead>
            <tbody>
              {details.map((item, idx) => {
                const isCorrect = item.actual === item.predicted;
                const diff = typeof item.actual === 'number' ? (1 - Math.abs(item.actual - item.predicted) / item.actual) * 100 : null;
                return (
                  <tr key={idx} style={{ borderBottom: "1px solid rgba(0,0,0,0.05)" }}>
                    <td style={{ padding: "1rem 0.75rem", fontSize: "0.9rem" }}>
                      <div style={{ fontWeight: "600" }}>{new Date(item.timestamp).toLocaleDateString()}</div>
                      <div style={{ fontSize: "0.75rem", opacity: 0.6 }}>{new Date(item.timestamp).toLocaleTimeString()}</div>
                    </td>
                    <td style={{ textAlign: "center", padding: "1rem 0.75rem", fontWeight: "700" }}>
                      {typeof item.actual === 'number' ? `$${item.actual.toLocaleString()}` : item.actual}
                    </td>
                    <td style={{ textAlign: "center", padding: "1rem 0.75rem", fontWeight: "700", color: "#3b82f6" }}>
                      {typeof item.predicted === 'number' ? `$${item.predicted.toLocaleString()}` : item.predicted}
                    </td>
                    <td style={{ textAlign: "right", padding: "1rem 0.75rem" }}>
                      <span style={{
                        padding: "0.25rem 0.5rem", borderRadius: "4px", fontSize: "0.75rem", fontWeight: "700",
                        background: (diff > 95 || isCorrect) ? "rgba(34,197,94,0.1)" : "rgba(245,158,11,0.1)",
                        color: (diff > 95 || isCorrect) ? "#16a34a" : "#d97706"
                      }}>
                        {diff !== null ? `${diff.toFixed(1)}% Match` : (isCorrect ? "MATCH" : "MISMATCH")}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {footnote && (
            <p style={{ marginTop: "1.25rem", fontSize: "0.75rem", color: "rgba(0,0,0,0.5)", fontStyle: "italic", lineHeight: 1.5 }}>
              {footnote}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
