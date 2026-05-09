import React from "react";
import { Activity, Upload, Wifi, ChevronRight, Info } from "lucide-react";
import { s, css } from "./DashboardStyles";

export default function SourceSelector({ setMode, setShowHowItWorks, setIsBatteryDemo }) {
  return (
    <section className="glass-panel">
      <div className="panel-header">
        <h2 className="panel-title">
          <Activity size={24} color="var(--accent-primary)" />
          Market Analysis — Choose Data Source
        </h2>
        <div
          style={{ ...s.pill, background: "rgba(59, 130, 246, 0.1)", border: "1px solid rgba(59, 130, 246, 0.3)", color: "var(--accent-primary)" }}
          className="icon-pill"
          onClick={() => setShowHowItWorks(true)}
        >
          <Info size={14} /><span>System Info</span>
        </div>
      </div>
      <div style={s.sourceGrid}>
        <div style={s.sourceCard} className="src-card" onClick={() => { setMode("upload"); setIsBatteryDemo(false); }}>
          <div style={s.iconWrap}><Upload size={36} color="var(--accent-primary)" /></div>
          <div style={s.srcLabel}>Upload Data</div>
          <div style={s.srcDesc}>Import your own dataset from a local file.<br /><span style={s.srcSub}>CSV · TSV · JSON · XLSX · XLS</span></div>
          <div style={s.srcAction}>Get Started <ChevronRight size={16} /></div>
        </div>
        <div style={{ ...s.sourceCard, border: "1px solid rgba(0, 214, 143, 0.3)" }} className="src-card" onClick={() => { setMode("upload"); setIsBatteryDemo(true); }}>
          <div style={s.iconWrap}><Activity size={36} color="#00d68f" /></div>
          <div style={s.srcLabel}>BESS Demo</div>
          <div style={s.srcDesc}>Hackathon-ready BESS Arbitrage demo.<br /><span style={{ ...s.srcSub, color: "#00d68f" }}>CSV Upload · LP Optimizer · Advanced AI</span></div>
          <div style={{ ...s.srcAction, color: "#00d68f" }}>Launch EMS <ChevronRight size={16} /></div>
        </div>
        <div style={s.sourceCard} className="src-card" onClick={() => setMode("api")}>
          <div style={s.iconWrap}><Wifi size={36} color="var(--accent-primary)" /></div>
          <div style={s.srcLabel}>Live API</div>
          <div style={s.srcDesc}>Connect to external market providers.<br /><span style={s.srcSub}>Twelve Data · EIA · Commodities</span></div>
          <div style={s.srcAction}>Connect <ChevronRight size={16} /></div>
        </div>
      </div>
      <style>{css}</style>
    </section>
  );
}
