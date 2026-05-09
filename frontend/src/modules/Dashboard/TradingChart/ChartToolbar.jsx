import React, { useState, useRef, useEffect } from 'react';
import { Settings2, Activity, ChevronDown } from 'lucide-react';
import { CHART_TYPES, INDICATORS, OSCILLATORS } from './chartTypes';

export default function ChartToolbar({
  onChartTypeChange,
  onAddMainIndicator,
  onAddSubIndicator,
  onStartDrawing,
  onClearDrawings,
  activeIndicators,
  activeOscillators,
  timeframe,
  interval,
  onTimeframeChange,
  onIntervalChange
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
      {/* ── First Row: Timing Controls ──────────────────── */}
      <div className="toolbar-row">
        <div className="control-group">
          <span className="group-label">View</span>
          <div className="timeframe-group">
            {['1W', '1M', '3M', '6M', '1Y', 'ALL'].map(tf => (
              <button 
                key={tf} 
                className={`time-btn ${timeframe === tf ? 'active' : ''}`}
                onClick={() => onTimeframeChange(tf)}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group">
          <span className="group-label">Interval</span>
          <div className="timeframe-group">
            {['1H', '4H', '1D'].map(iv => (
              <button 
                key={iv} 
                className={`time-btn ${interval === iv ? 'active' : ''}`}
                onClick={() => onIntervalChange(iv)}
              >
                {iv}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Second Row: Analysis Tools ──────────────────── */}
      <div className="toolbar-row secondary-row">
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
      </div>

      {/* ── Inline CSS (scoped) ─────────────────────────── */}
      <style>{`
        .chart-toolbar {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          padding: 0.5rem 0;
          position: relative;
          z-index: 60;
        }
        .toolbar-row { display: flex; gap: 0.5rem; align-items: flex-end; flex-wrap: wrap; }
        .secondary-row { padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.05); }
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
        .tb-icon { width: 1.2rem; text-align: center; font-size: 0.8rem; opacity: 0.6; }

        /* Unified Timing Controls Style */
        .control-group { display: flex; flex-direction: column; gap: 4px; margin-left: 0.5rem; }
        .group-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; padding-left: 4px; }
        .timeframe-group { display: flex; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 2px; border: 1px solid var(--border-color); }
        .time-btn { 
            background: transparent; border: none; color: var(--text-secondary); 
            padding: 0.35rem 0.65rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;
            cursor: pointer; transition: 0.2s;
        }
        .time-btn:hover { color: var(--text-primary); background: rgba(255,255,255,0.05); }
        .time-btn.active { background: #3b82f6; color: #fff; }
      `}</style>
    </div>
  );
}
