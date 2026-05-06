import React, { useState, useRef, useEffect } from 'react';
import { Settings2, Activity, PenTool, X, ChevronDown } from 'lucide-react';
import { CHART_TYPES, INDICATORS, OSCILLATORS, DRAWING_TOOLS } from './chartTypes';

export default function ChartToolbar({
  onChartTypeChange,
  onAddMainIndicator,
  onAddSubIndicator,
  onStartDrawing,
  onClearDrawings,
  activeIndicators,
  activeOscillators,
}) {
  const [openMenu, setOpenMenu] = useState(null); // 'type' | 'indicators' | 'draw' | null

  // Close menu on outside click
  const toolbarRef = useRef(null);
  useEffect(() => {
    function handleClick(e) {
      if (toolbarRef.current && !toolbarRef.current.contains(e.target)) setOpenMenu(null);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const toggle = (menu) => setOpenMenu(openMenu === menu ? null : menu);

  return (
    <div ref={toolbarRef} className="chart-toolbar">

      {/* ── Chart Type ──────────────────────────────────── */}
      <div className="tb-dropdown-wrapper">
        <button className="tb-btn" onClick={() => toggle('type')}>
          <Settings2 size={15} /> Chart Type <ChevronDown size={14} />
        </button>
        {openMenu === 'type' && (
          <div className="tb-dropdown">
            <div className="tb-dropdown-title">Chart Type</div>
            {CHART_TYPES.map(t => (
              <button key={t.id} className="tb-dropdown-item" onClick={() => { onChartTypeChange(t.id); setOpenMenu(null); }}>
                <span className="tb-icon">{t.icon}</span> {t.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ── Indicators Dropdown ────────────────────────── */}
      <div className="tb-dropdown-wrapper">
        <button className="tb-btn" onClick={() => toggle('indicators_only')}>
          <Activity size={15} /> Indicators <ChevronDown size={14} />
        </button>
        {openMenu === 'indicators_only' && (
          <div className="tb-dropdown">
            <div className="tb-dropdown-title">Main Indicators</div>
            {INDICATORS.map(ind => {
              const isActive = activeIndicators.includes(ind.id);
              return (
                <button 
                  key={ind.id + ind.label} 
                  className={`tb-dropdown-item ${isActive ? 'tb-active' : ''}`} 
                  onClick={() => onAddMainIndicator(ind.id)}
                >
                  {ind.label} {isActive && <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>✓</span>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Oscillators Dropdown ────────────────────────── */}
      <div className="tb-dropdown-wrapper">
        <button className="tb-btn" onClick={() => toggle('oscillators_only')}>
          <Activity size={15} /> Oscillators <ChevronDown size={14} />
        </button>
        {openMenu === 'oscillators_only' && (
          <div className="tb-dropdown">
            <div className="tb-dropdown-title">Technical Oscillators</div>
            {OSCILLATORS.map(osc => {
              const isActive = activeOscillators.includes(osc.id);
              return (
                <button 
                  key={osc.id} 
                  className={`tb-dropdown-item ${isActive ? 'tb-active' : ''}`} 
                  onClick={() => onAddSubIndicator(osc.id)}
                >
                  {osc.label} {isActive && <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>✓</span>}
                </button>
              );
            })}
          </div>
        )}
      </div>


      {/* Drawing tools are now handled natively by Plotly in the chart modebar */}


      {/* ── Inline CSS (scoped) ─────────────────────────── */}
      <style>{`
        .chart-toolbar {
          display: flex;
          gap: 0.5rem;
          align-items: center;
          padding: 0.5rem 0;
          flex-wrap: wrap;
          position: relative;
          z-index: 60;
        }
        .tb-dropdown-wrapper { position: relative; }
        .tb-btn {
          display: flex;
          align-items: center;
          gap: 0.35rem;
          background: rgba(128,128,128,0.08);
          border: 1px solid var(--border-color);
          color: var(--text-primary);
          padding: 0.45rem 0.8rem;
          border-radius: 6px;
          font-family: var(--font-body);
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.15s;
        }
        .tb-btn:hover { background: var(--bg-panel-hover); border-color: var(--border-focus); }
        .tb-dropdown {
          position: absolute;
          top: calc(100% + 6px);
          left: 0;
          min-width: 220px;
          background: var(--bg-panel);
          border: 1px solid var(--border-color);
          border-radius: 10px;
          padding: 0.5rem;
          backdrop-filter: blur(24px);
          box-shadow: 0 8px 30px rgba(0,0,0,0.35);
          z-index: 200;
          max-height: 420px;
          overflow-y: auto;
        }
        .tb-dropdown-wide { min-width: 440px; }
        .tb-dropdown-columns { display: flex; gap: 0.75rem; }
        .tb-dropdown-col { flex: 1; min-width: 0; }
        .tb-dropdown-title {
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-secondary);
          padding: 0.4rem 0.5rem 0.25rem;
          font-weight: 600;
        }
        .tb-dropdown-item {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          width: 100%;
          text-align: left;
          background: transparent;
          border: none;
          color: var(--text-primary);
          padding: 0.45rem 0.5rem;
          border-radius: 5px;
          cursor: pointer;
          font-family: var(--font-body);
          font-size: 0.85rem;
          transition: background 0.12s;
        }
        .tb-dropdown-item:hover { background: var(--bg-panel-hover); color: var(--accent-primary); }
        .tb-active { background: rgba(var(--accent-primary-rgb), 0.12); color: var(--accent-primary); font-weight: 600; }
        .tb-danger { color: var(--danger) !important; font-weight: 600; }

        .tb-danger:hover { background: rgba(239,68,68,0.1) !important; }
        .tb-divider { height: 1px; background: var(--border-color); margin: 0.3rem 0; }
        .tb-icon { width: 1.2rem; text-align: center; font-size: 0.8rem; opacity: 0.6; }
      `}</style>
    </div>
  );
}
