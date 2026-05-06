import React from "react";
import { BrainCircuit, Clock, Loader } from "lucide-react";

export default function Forecaster({ plotlyHtml, predictionResult, isPredicting, isLoadingChart }) {
  const forecastHtml = plotlyHtml?.forecast;

  return (
    <section className="glass-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div className="panel-header" style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border-color)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h2 className="panel-title" style={{ fontSize: "1.1rem", margin: 0, display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <BrainCircuit size={22} color="var(--accent-secondary)" />
          AI Price Forecast
        </h2>
        {predictionResult && predictionResult.feature_importance && (
          <>
            <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" }}>
              {predictionResult.training_score !== undefined && (
                <div style={{ 
                  padding: "0.35rem 0.75rem", 
                  borderRadius: "20px", 
                  background: "rgba(34, 197, 94, 0.15)", 
                  border: "1px solid rgba(34, 197, 94, 0.4)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}>
                  <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 10px #22c55e" }} />
                  <span style={{ fontSize: "0.85rem", color: "#22c55e", fontWeight: "700" }}>
                    Training: {predictionResult.training_score}%
                  </span>
                </div>
              )}

              {predictionResult.validation_score !== undefined && (
                <div style={{ 
                  padding: "0.35rem 0.75rem", 
                  borderRadius: "20px", 
                  background: "rgba(6, 182, 212, 0.1)", 
                  border: "1px solid rgba(6, 182, 212, 0.3)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}>
                  <span style={{ fontSize: "0.78rem", color: "#06b6d4", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.02em" }}>
                    Validation: <span style={{ color: "var(--text-primary)" }}>{predictionResult.validation_score}%</span>
                  </span>
                </div>
              )}

              {predictionResult.check_score !== undefined && (
                <div style={{ 
                  padding: "0.35rem 0.75rem", 
                  borderRadius: "20px", 
                  background: "rgba(245, 158, 11, 0.1)", 
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}>
                  <span style={{ fontSize: "0.78rem", color: "#d97706", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.02em" }}>
                    Check: <span style={{ color: "var(--text-primary)" }}>{predictionResult.check_score}%</span>
                  </span>
                </div>
              )}
            </div>

            <div style={{ display: "flex", gap: "1rem" }}>
              {Object.entries(predictionResult.feature_importance).slice(0, 3).map(([k, v]) => (
                <div key={k} style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                  <span style={{ textTransform: "uppercase", opacity: 0.7 }}>{k}:</span> 
                  <span style={{ marginLeft: "0.25rem", color: "var(--accent-secondary)", fontWeight: "600" }}>{typeof v === 'number' ? v.toFixed(2) : v}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Body */}
      <div style={{ flex: 1, position: "relative", minHeight: "340px" }}>
        {isPredicting || (predictionResult && !forecastHtml && isLoadingChart) ? (
          <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1rem" }}>
            <Loader className="spin" size={40} color="var(--accent-secondary)" />
            <span style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              {isPredicting ? "AI Model Training & Predicting..." : "Generating Forecast Visualization..."}
            </span>
          </div>
        ) : forecastHtml ? (
          <div style={{ height: "100%", padding: "1rem" }}>
            <iframe
              srcDoc={forecastHtml}
              style={{ width: "100%", height: "300px", border: "none", borderRadius: "8px" }}
              title="AI Forecast Plot"
            />
            {predictionResult?.points && predictionResult.points.length > 0 && (
              <div style={{ marginTop: "1rem", padding: "1rem", background: "rgba(128,128,128,0.05)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
                <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
                  <span>Next Predicted Price:</span>
                  <span style={{ color: "var(--accent-secondary)", fontWeight: "700" }}>${predictionResult.points[0].forecast.toLocaleString()}</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Placeholder body */
          <div style={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "1.25rem",
            padding: "2rem",
          }}>
            {/* Pulsing icon */}
            <div style={{
              width: "64px",
              height: "64px",
              borderRadius: "50%",
              background: "rgba(6,182,212,0.08)",
              border: "2px solid rgba(6,182,212,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              animation: "forecastPulse 2.4s ease-in-out infinite",
            }}>
              <Clock size={28} color="var(--accent-secondary)" style={{ opacity: 0.75 }} />
            </div>

            <div style={{ textAlign: "center" }}>
              <p style={{
                fontSize: "1rem",
                fontWeight: "600",
                color: "var(--text-primary)",
                fontFamily: "var(--font-display)",
                marginBottom: "0.4rem",
              }}>
                Waiting for Data &amp; Settings
              </p>
              <p style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                lineHeight: 1.6,
                maxWidth: "240px",
              }}>
                Configure model settings and run prediction to see the AI forecast here.
              </p>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes forecastPulse {
          0%, 100% { transform: scale(1);   opacity: 1; }
          50%       { transform: scale(1.08); opacity: 0.7; }
        }
      `}</style>
    </section>
  );
}
