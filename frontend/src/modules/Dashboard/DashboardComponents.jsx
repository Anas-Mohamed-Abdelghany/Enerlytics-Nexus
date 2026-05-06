import React, { useState, useEffect, useRef } from "react";
import { ChevronDown, AlertTriangle } from "lucide-react";
import { s } from "./DashboardStyles";

// ─── Error Boundary ───────────────────────────────────────────────────────────
export class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(e) { return { error: e }; }
  render() {
    if (this.state.error) return (
      <div style={s.errorBox}>
        <AlertTriangle size={18} />
        <div>
          <strong>Chart render error:</strong> {this.state.error.message}
          <br />
          <span style={s.retryPill} onClick={() => this.setState({ error: null })}>Retry</span>
        </div>
      </div>
    );
    return this.props.children;
  }
}

// ─── Modern Select ────────────────────────────────────────────────────────────
export const ModernSelect = ({ value, onChange, options, placeholder = "Select..." }) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setIsOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selectedLabel = options.find(o => o.value === value)?.label || value || placeholder;

  return (
    <div ref={containerRef} className="modern-select-container">
      <div
        className={`modern-select-trigger ${isOpen ? "active" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedLabel}</span>
        <ChevronDown size={18} className={`arrow ${isOpen ? "open" : ""}`} />
      </div>
      {isOpen && (
        <div className="modern-select-dropdown">
          {options.map(opt => (
            <div
              key={opt.value}
              className={`modern-select-option ${value === opt.value ? "selected" : ""}`}
              onClick={() => { onChange(opt.value); setIsOpen(false); }}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
