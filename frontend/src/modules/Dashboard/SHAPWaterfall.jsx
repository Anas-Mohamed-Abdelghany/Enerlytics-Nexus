import React from "react";
import { TrendingUp, TrendingDown, HelpCircle } from "lucide-react";

export default function SHAPWaterfall({ metadata, predictionType }) {
  if (!metadata || !metadata.contributions) return null;

  const { base_value, contributions } = metadata;
  const entries = Object.entries(contributions)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 6);

  const totalContribution = Object.values(contributions).reduce((a, b) => a + b, 0);
  const finalValue = base_value + totalContribution;

  return (
    <div className="glass-panel" style={{ marginTop: "1rem", padding: "1.5rem", border: "1px solid var(--border-color)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <div>
          <h3 style={{ fontSize: "1.1rem", margin: 0, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            SHAP Waterfall Explainability
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", margin: 0 }}>
            How each feature pushed the prediction away from the historical average
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase" }}>Base Value</div>
          <div style={{ fontSize: "1rem", fontWeight: "700", color: "var(--text-primary)" }}>
            {predictionType === 'regression' ? `$${base_value.toLocaleString()}` : base_value.toFixed(3)}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {entries.map(([feature, val]) => {
          const isPositive = val > 0;
          return (
            <div key={feature} style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <div style={{ width: "140px", fontSize: "0.8rem", color: "var(--text-primary)", fontWeight: "500", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {feature}
              </div>
              
              <div style={{ flex: 1, display: "flex", alignItems: "center", position: "relative", height: "24px" }}>
                {/* Zero line */}
                <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: "1px", background: "var(--border-color)", zIndex: 1 }} />
                
                {/* Contribution bar */}
                <div style={{ 
                  position: "absolute",
                  left: isPositive ? "50%" : `calc(50% - ${Math.min(45, Math.abs(val) * 100)}%)`,
                  width: `${Math.min(45, Math.abs(val) * 100)}%`,
                  height: "14px",
                  background: isPositive ? "rgba(34, 197, 94, 0.6)" : "rgba(239, 68, 68, 0.6)",
                  borderRadius: "4px",
                  border: `1px solid ${isPositive ? "#22c55e" : "#ef4444"}`,
                  zIndex: 2
                }} />
              </div>

              <div style={{ width: "60px", textAlign: "right", fontSize: "0.8rem", fontWeight: "700", color: isPositive ? "#22c55e" : "#ef4444" }}>
                {isPositive ? "+" : ""}{predictionType === 'regression' ? val.toFixed(2) : val.toFixed(3)}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ 
        marginTop: "1.25rem", 
        paddingTop: "1rem", 
        borderTop: "1px solid var(--border-color)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
          <HelpCircle size={14} />
          <span>Sum of all contributions + Base Value = Final Prediction</span>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "0.7rem", color: "var(--accent-secondary)", fontWeight: "700", textTransform: "uppercase" }}>Final Prediction</div>
          <div style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--accent-secondary)" }}>
            {predictionType === 'regression' ? `$${finalValue.toLocaleString()}` : finalValue.toFixed(3)}
          </div>
        </div>
      </div>
    </div>
  );
}
