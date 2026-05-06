import React from "react";
import { Upload, RotateCcw, AlertTriangle, FileText } from "lucide-react";
import { s, css } from "./DashboardStyles";
import { ACCEPTED } from "./useDashboard";

export default function UploadView({ fileRef, dragOver, setDragOver, onDrop, onFileChange, error, reset }) {
  return (
    <section className="glass-panel">
      <div className="panel-header">
        <h2 className="panel-title"><Upload size={22} color="var(--accent-primary)" /> Upload Market Data</h2>
        <div style={s.pill} className="icon-pill" onClick={reset}><RotateCcw size={14} /><span>Change Source</span></div>
      </div>
      <div
        style={{ ...s.dropZone, ...(dragOver ? s.dropActive : {}) }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input ref={fileRef} type="file" accept={ACCEPTED} style={{ display: "none" }} onChange={onFileChange} />
        <div style={s.dropContent}>
          <Upload size={48} color="var(--accent-primary)" style={{ opacity: 0.7 }} />
          <p style={s.dropTitle}>Drag &amp; drop your file here</p>
          <p style={s.dropSub}>or click to browse</p>
          <div style={s.badges}>
            {["CSV", "TSV", "JSON", "XLSX", "XLS"].map((f) => <span key={f} style={s.badge}>{f}</span>)}
          </div>
        </div>
      </div>
      {error && <div style={s.errorBox}><AlertTriangle size={18} /><div><strong>Error:</strong> {error}</div></div>}
      <div style={s.hintBox}>
        <FileText size={16} style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Expected columns</strong> (case-insensitive):&nbsp;
          {["timestamp/date/time", "open", "high", "low", "close", "volume"].map((c) => <code key={c} style={s.code}>{c}</code>)}
          <br /><em style={{ opacity: 0.65, fontSize: "0.8rem" }}>Only <strong>date</strong> and <strong>close</strong> are required.</em>
        </div>
      </div>
      <style>{css}</style>
    </section>
  );
}
