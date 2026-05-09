import React from "react";
import { AlertTriangle, UploadCloud } from "lucide-react";
import { s, css } from "./DashboardStyles";

export default function UploadView({ 
  trainFileRef, testFileRef, 
  onUploadTrain, onUploadTest, 
  onUseSavedTrain,
  loadingTrain, loadingTest,
  trainStatus,
  error 
}) {
  return (
    <section style={{ padding: 0 }}>
      <div style={s.sectionHeader}>
        <h2 style={s.sectionTitle}>Data Pipeline</h2>
      </div>

      <div style={s.uploadGrid}>
        {/* TRAIN ROW */}
        <div 
          className="hero-card" 
          style={{ ...s.uploadCell, ...s.trainCell }}
          onClick={() => trainFileRef.current?.click()}
        >
          <input ref={trainFileRef} type="file" style={{ display: "none" }} onChange={(e) => onUploadTrain(e.target.files[0])} />
          
          <div style={s.cellInfo}>
            <span style={s.cellTitle}>TRAIN</span>
            <span style={s.cellDataYear}>2024 data</span>
            <span style={s.cellDesc}>Tune forecasting model</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
            <button 
              style={{ 
                ...s.quickPathBtn, 
                backgroundColor: trainStatus === 'success' ? '#10b981' : trainStatus === 'error' ? '#ef4444' : s.quickPathBtn.background,
                borderColor: trainStatus === 'success' ? '#059669' : trainStatus === 'error' ? '#dc2626' : s.quickPathBtn.border
              }}
              onClick={(e) => { e.stopPropagation(); onUseSavedTrain(); }}
            >
              {trainStatus === 'success' ? 'Loaded ✓' : trainStatus === 'error' ? 'Failed ✗' : 'Load Saved'}
            </button>
            {loadingTrain && <div className="spin" style={{ width: '16px', height: '16px', border: '2px solid rgba(245,158,11,0.3)', borderTopColor: '#f59e0b', borderRadius: '50%' }} />}
          </div>
        </div>

        {/* TEST ROW */}
        <div 
          className="hero-card" 
          style={{ ...s.uploadCell, ...s.testCell }}
          onClick={() => testFileRef.current?.click()}
        >
          <input ref={testFileRef} type="file" style={{ display: "none" }} onChange={(e) => onUploadTest(e.target.files[0])} />
          
          <div style={s.cellInfo}>
            <span style={s.cellTitle}>TEST</span>
            <span style={s.cellDataYear}>2025 data</span>
            <span style={s.cellDesc}>Report & optimization</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center' }}>
            <UploadCloud size={20} color="rgba(255,255,255,0.2)" />
            {loadingTest && <div className="spin" style={{ marginLeft: '0.5rem', width: '16px', height: '16px', border: '2px solid rgba(245,158,11,0.3)', borderTopColor: '#f59e0b', borderRadius: '50%' }} />}
          </div>
        </div>
      </div>

      {error && <div style={s.errorBox}><AlertTriangle size={14} /><div><strong>Pipeline Error:</strong> {error}</div></div>}

      <div style={s.warningBox}>
        <AlertTriangle size={16} style={{ flexShrink: 0 }} />
        <div>
          Anomaly detected in 2025 data. Reconstruct SoC before optimising.
        </div>
      </div>

      <div style={s.settingsDivider} />
      <style>{css}</style>
    </section>
  );
}
