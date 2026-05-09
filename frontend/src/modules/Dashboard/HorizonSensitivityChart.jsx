import React from "react";
import { TrendingDown, Info, ShieldCheck } from "lucide-react";

export default function HorizonSensitivityChart({ data }) {
  if (!data || data.length === 0) return null;

  const width = 400;
  const height = 120;
  const padding = 30;

  const getX = (i) => (i / (data.length - 1)) * (width - 2 * padding) + padding;
  const getY = (val) => height - ((val - 70) / 30) * (height - 2 * padding) - padding;

  const linePath = data.map((d, i) => `${getX(i)},${getY(d.accuracy)}`).join(" L ");

  return (
    <div className="glass-panel" style={{ marginTop: "1rem", padding: "1.25rem", background: "rgba(128,128,128,0.02)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h3 style={{ fontSize: "0.95rem", margin: 0, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <TrendingDown size={18} color="var(--accent-primary)" />
            Confidence Decay Analysis
          </h3>
          <p style={{ fontSize: "0.7rem", color: "var(--text-secondary)", margin: 0 }}>Model accuracy vs. prediction horizon (timesteps)</p>
        </div>
        <div style={{ 
          background: "rgba(59, 130, 246, 0.1)", 
          padding: "0.25rem 0.5rem", 
          borderRadius: "6px", 
          fontSize: "0.7rem", 
          color: "var(--accent-primary)",
          fontWeight: "700"
        }}>
          HORIZON SENSITIVITY
        </div>
      </div>

      <div style={{ position: "relative", width: "100%", height: `${height}px` }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "100%" }} preserveAspectRatio="none">
          {/* Grid lines */}
          {[70, 80, 90, 100].map(val => (
            <g key={val}>
              <line x1={padding} y1={getY(val)} x2={width - padding} y2={getY(val)} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
              <text x="5" y={getY(val) + 3} fill="var(--text-secondary)" fontSize="8" opacity="0.5">{val}%</text>
            </g>
          ))}
          
          {/* Decay line */}
          <path d={`M ${linePath}`} fill="none" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" />
          
          {/* Data points */}
          {data.map((d, i) => (
            <g key={i}>
              <circle cx={getX(i)} cy={getY(d.accuracy)} r="3" fill="var(--accent-primary)" />
              <text x={getX(i)} y={height - 5} fill="var(--text-secondary)" fontSize="8" textAnchor="middle">{d.horizon}h</text>
            </g>
          ))}
        </svg>
      </div>

      <div style={{ marginTop: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.7rem", color: "var(--text-secondary)", fontStyle: "italic" }}>
        <ShieldCheck size={14} color="#22c55e" />
        <span>Insight: Accuracy remains above 85% for the first 16 hours. High reliability for daily cycles.</span>
      </div>
    </div>
  );
}
