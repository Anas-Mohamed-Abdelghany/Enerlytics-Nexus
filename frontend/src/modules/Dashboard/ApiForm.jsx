import React from "react";
import { Wifi, RotateCcw, AlertTriangle } from "lucide-react";
import { s, css } from "./DashboardStyles";
import { ModernSelect } from "./DashboardComponents";

export default function ApiForm({
  apiChoice, setApiChoice, ticker, setTicker, tickerMap,
  startDate, setStartDate, endDate, setEndDate,
  fetchInterval, setFetchInterval, handleApiFetch, error, reset
}) {
  return (
    <section className="glass-panel">
      <div className="panel-header">
        <h2 className="panel-title"><Wifi size={22} color="var(--accent-primary)" /> Fetch Live Data</h2>
        <div style={s.pill} className="icon-pill" onClick={reset}><RotateCcw size={14} /><span>Change Source</span></div>
      </div>

      <div style={s.apiForm}>
        <div style={s.formGroup}>
          <label style={s.label}>API Provider</label>
          <ModernSelect value={apiChoice} onChange={setApiChoice} options={[
            { label: "Alpha Vantage", value: "Alpha Vantage" },
            { label: "Financial Modeling Prep", value: "Financial Prep" },
            { label: "Polygon", value: "Polygon" },
            { label: "Twelve Data", value: "Twelve Data" },
            { label: "EOD Historical Data", value: "EOD" },
            { label: "Ember Energy", value: "Ember Energy" },
            { label: "MetalpriceAPI", value: "MetalpriceAPI" },
            { label: "ForexRateAPI", value: "ForexRateAPI" },
            { label: "U.S. Energy Info Admin (EIA)", value: "EIA" },
            { label: "Oil Price API", value: "Oil Price API" }
          ]} />
        </div>
        <div style={s.formGroup}>
          <label style={s.label}>Company / Ticker</label>
          <ModernSelect value={ticker} onChange={setTicker} options={[
            ...(tickerMap[apiChoice] || []),
            { label: "-- Custom Symbol --", value: "CUSTOM" }
          ]} />
        </div>
        {ticker === "CUSTOM" && (
          <div style={s.formGroup}>
            <label style={s.label}>Enter Custom Ticker</label>
            <input style={s.input} type="text" placeholder="e.g. MSFT" onChange={e => setTicker(e.target.value.toUpperCase())} />
          </div>
        )}
        <div style={s.formGroup}>
          <label style={s.label}>Start Date</label>
          <input style={s.input} type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </div>
        <div style={s.formGroup}>
          <label style={s.label}>End Date</label>
          <input style={s.input} type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </div>
        <div style={s.formGroup}>
          <label style={s.label}>Data Interval</label>
          <ModernSelect value={fetchInterval} onChange={setFetchInterval} options={
            ["Ember Energy", "EIA"].includes(apiChoice)
              ? [{ label: "Monthly", value: "1M" }, { label: "Annual", value: "1Y" }]
              : [{ label: "Daily", value: "1D" }, { label: "Weekly", value: "1W" }, { label: "Monthly", value: "1M" }, { label: "Annual", value: "1Y" }]
          } />
        </div>
        <button style={s.submitBtn} className="submit-btn" onClick={handleApiFetch}>
          <Wifi size={16} /> Fetch Market Data
        </button>

        {["Oil Price API", "MetalpriceAPI", "ForexRateAPI"].includes(apiChoice) && (
          <div style={{...s.errorBox, backgroundColor: "rgba(59, 130, 246, 0.1)", borderColor: "rgba(59, 130, 246, 0.3)", color: "var(--accent-primary)", marginTop: "1rem"}}>
            <AlertTriangle size={18} />
            <div><strong>Note:</strong> The {apiChoice} (Free Tier) only provides data for the <strong>{apiChoice === "ForexRateAPI" ? "past 5 days" : "past 30 days"}</strong>.</div>
          </div>
        )}
      </div>

      {error && <div style={s.errorBox}><AlertTriangle size={18} /><div><strong>Error:</strong> {error}</div></div>}
      <style>{css}</style>
    </section>
  );
}
