import React from "react";
import { Activity, Brain, ChevronDown, ChevronUp } from "lucide-react";

import SHAPWaterfall from "./SHAPWaterfall";
import BatteryDashboard from "./BatteryDashboard";

export default function AIIntelligenceReports({
  predictionResult,
  predictionType,
  checkSamples,
  showValidationDetails,
  setShowValidationDetails,
  showRobustnessDetails,
  setShowRobustnessDetails,
  // Battery Props
  priceMatrix,
  predicting
}) {
  if (!predictionResult) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* XAI SHAP Waterfall & Feature Importance */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "1.5rem" }}>
        {predictionResult.shap_metadata ? (
          <SHAPWaterfall metadata={predictionResult.shap_metadata} predictionType={predictionType} />
        ) : predictionResult.feature_importance && (
          <div className="glass-panel" style={{ padding: "1.5rem", background: 'rgba(255,255,255,0.02)' }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
              <Brain size={20} color="#3b82f6" /> Explainable AI (XAI): Feature Importance
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {Object.entries(predictionResult.feature_importance).sort((a, b) => b[1] - a[1]).map(([key, val]) => (
                <div key={key} style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                  <div style={{ width: "140px", fontSize: "0.85rem", color: "var(--text-primary)" }}>{key.replace('_', ' ')}</div>
                  <div style={{ flex: 1, height: "8px", background: "rgba(128,128,128,0.1)", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${val * 100}%`, background: "#3b82f6", borderRadius: "4px" }} />
                  </div>
                  <div style={{ width: "50px", fontSize: "0.85rem", color: "#3b82f6", fontWeight: "600", textAlign: 'right' }}>{(val * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Validation Report */}
      {predictionResult.validation_details && (
        <ValidationReport
          details={predictionResult.validation_details.filter(d => d.type === 'VALIDATION')}
          show={showValidationDetails}
          setShow={setShowValidationDetails}
          title="AI Validation Integrity Report"
          subtitle="Hold-out Set (Latest 10% Unseen Data)"
          color="#3b82f6"
          lastColLabel="Integrity"
        />
      )}

      {/* Robustness Report */}
      {predictionResult.validation_details && (
        <ValidationReport
          details={predictionResult.validation_details.filter(d => d.type === 'CHECK')}
          show={showRobustnessDetails}
          setShow={setShowRobustnessDetails}
          title="AI Robustness Check Report"
          subtitle={`Historical Random Segments (${checkSamples} Samples)`}
          color="#f59e0b"
          lastColLabel="Consistency"
          footnote="*This report validates model consistency by re-running analysis on random historical segments. Higher consistency scores indicate a model that has successfully generalized the market's behavior."
        />
      )}
    </div>
  );
}

function ValidationReport({ details, show, setShow, title, subtitle, color, lastColLabel, footnote }) {
  if (!details || details.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: "1.5rem", background: 'rgba(255,255,255,0.02)' }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: show ? "1.5rem" : "0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
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
          <table style={{ width: "100%", borderCollapse: "collapse", color: "var(--text-primary)" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--border-color)" }}>
                <th style={{ textAlign: "left", padding: "0.75rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>Date</th>
                <th style={{ textAlign: "center", padding: "0.75rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>Actual Outcome</th>
                <th style={{ textAlign: "center", padding: "0.75rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>AI Prediction</th>
                <th style={{ textAlign: "right", padding: "0.75rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>{lastColLabel}</th>
              </tr>
            </thead>
            <tbody>
              {details.map((item, idx) => {
                const isCorrect = item.actual === item.predicted;
                const diff = typeof item.actual === 'number' ? (1 - Math.abs(item.actual - item.predicted) / item.actual) * 100 : null;
                return (
                  <tr key={idx} style={{ borderBottom: "1px solid var(--border-color)" }}>
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
            <p style={{ marginTop: "1.25rem", fontSize: "0.75rem", color: "var(--text-secondary)", fontStyle: "italic", lineHeight: 1.5 }}>
              {footnote}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
