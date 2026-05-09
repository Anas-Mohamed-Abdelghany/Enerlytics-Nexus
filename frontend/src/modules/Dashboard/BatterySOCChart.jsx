import React from "react";
import { Battery, Zap, DollarSign, Activity } from "lucide-react";

export default function BatterySOCChart({ simulation }) {
  if (!simulation || !simulation.soc_points || simulation.soc_points.length === 0) return null;

  const { soc_points, actions, total_revenue, final_soc } = simulation;
  
  const width = 1000;
  const height = 150;
  const padding = 20;
  
  const getX = (i) => (i / (soc_points.length - 1)) * (width - 2 * padding) + padding;
  const getY = (val) => height - (val / 100) * (height - 2 * padding) - padding;

  const linePath = soc_points.map((val, i) => `${getX(i)},${getY(val)}`).join(" L ");
  const areaPath = `M ${padding},${height - padding} L ${linePath} L ${width - padding},${height - padding} Z`;

  return (
    <div className="glass-panel" style={{ marginTop: "1.5rem", padding: "1.5rem", background: "rgba(128,128,128,0.03)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{ 
            background: "rgba(34, 197, 94, 0.1)", 
            padding: "0.5rem", 
            borderRadius: "10px", 
            border: "1px solid rgba(34, 197, 94, 0.2)" 
          }}>
            <Battery size={20} color="#22c55e" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.1rem", margin: 0, color: "var(--text-primary)" }}>BESS State-of-Charge (SOC) Simulation</h3>
            <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", margin: 0 }}>Arbitrage strategy behavior over forecast horizon</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "1.5rem" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Grid Baseline</div>
            <div style={{ fontSize: "1rem", fontWeight: "600", color: "var(--text-secondary)", textDecoration: "line-through", opacity: 0.6 }}>
              ${simulation.baseline_cost?.toLocaleString()}
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "0.7rem", color: simulation.savings >= 0 ? "#22c55e" : "#ef4444", fontWeight: "800", textTransform: "uppercase", letterSpacing: "0.05em" }}>Net Savings</div>
            <div style={{ fontSize: "1.2rem", fontWeight: "800", color: simulation.savings >= 0 ? "#22c55e" : "#ef4444", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <DollarSign size={18} />
              {simulation.savings?.toLocaleString()}
              <span style={{ 
                fontSize: "0.8rem", 
                background: simulation.savings >= 0 ? "rgba(34, 197, 94, 0.1)" : "rgba(239, 68, 68, 0.1)", 
                padding: "2px 6px", 
                borderRadius: "4px", 
                marginLeft: "4px",
                color: simulation.savings >= 0 ? "#22c55e" : "#ef4444"
              }}>
                {simulation.savings_pct > 0 ? "+" : ""}{simulation.savings_pct}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SVG Timeline */}
      <div style={{ position: "relative", width: "100%", height: `${height}px`, background: "rgba(0,0,0,0.2)", borderRadius: "12px", border: "1px solid var(--border-color)", overflow: "hidden" }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "100%" }} preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map(level => (
            <line 
              key={level}
              x1={padding} y1={getY(level)} x2={width - padding} y2={getY(level)}
              stroke="rgba(255,255,255,0.05)" strokeWidth="1"
            />
          ))}
          
          {/* Area under curve */}
          <path d={areaPath} fill="url(#socGradient)" opacity="0.3" />
          
          {/* Main SOC line */}
          <path d={`M ${linePath}`} fill="none" stroke="var(--accent-secondary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          
          {/* Action Markers */}
          {actions.map((action, i) => {
            if (action.type === "IDLE") return null;
            return (
              <circle 
                key={i}
                cx={getX(i)} cy={getY(soc_points[i+1])}
                r="4"
                fill={action.type === "CHARGE" ? "#22c55e" : "#ef4444"}
                filter="drop-shadow(0 0 4px rgba(0,0,0,0.5))"
              />
            );
          })}

          <defs>
            <linearGradient id="socGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-secondary)" />
              <stop offset="100%" stopColor="transparent" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Legend & Summary */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "1rem" }}>
        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem", color: "var(--text-secondary)" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e" }} /> Charge
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem", color: "var(--text-secondary)" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444" }} /> Discharge
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem", color: "var(--text-secondary)" }}>
            <div style={{ width: "12px", height: "2px", background: "var(--accent-secondary)" }} /> State of Charge (%)
          </div>
        </div>
        
        <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontStyle: "italic" }}>
          *Simulation assumes 100kWh capacity / 50kW max power / 90% efficiency
        </div>
      </div>
    </div>
  );
}
