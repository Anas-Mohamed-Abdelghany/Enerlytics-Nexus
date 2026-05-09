// ─── Dashboard Styles ─────────────────────────────────────────────────────────
export const s = {
  content: { flex: 1, minHeight: 0, position: "relative", display: "flex", flexDirection: "column" },
  chartOverlay: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.5)", zIndex: 10, borderRadius: "12px" },
  emptyState: { flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-secondary)", fontSize: "1.1rem" },
  sourceGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: "1.5rem", marginTop: "1rem" },
  sourceCard: { background: "rgba(128,128,128,0.06)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "2rem 1.75rem", display: "flex", flexDirection: "column", alignItems: "flex-start", gap: "0.75rem", cursor: "pointer", textAlign: "left", color: "var(--text-primary)", transition: "all 0.2s ease", fontFamily: "var(--font-body)" },
  cardDisabled: { cursor: "not-allowed", opacity: 0.6 },
  iconWrap: { background: "rgba(59,130,246,0.08)", borderRadius: "12px", padding: "0.9rem", marginBottom: "0.25rem" },
  srcLabel: { fontSize: "1.2rem", fontWeight: "700", fontFamily: "var(--font-display)", letterSpacing: "-0.02em" },
  srcDesc: { fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: 1.6, flex: 1 },
  srcSub: { fontFamily: "monospace", fontSize: "0.8rem", color: "var(--accent-primary)", opacity: 0.85 },
  srcAction: { display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.85rem", fontWeight: "600", color: "var(--accent-primary)", marginTop: "0.5rem" },
  pill: { display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.32rem 0.8rem", borderRadius: "20px", background: "rgba(128,128,128,0.07)", border: "1px solid var(--border-color)", color: "var(--text-secondary)", fontSize: "0.8rem", fontFamily: "var(--font-body)", cursor: "pointer", transition: "all 0.15s", userSelect: "none" },
  retryPill: { display: "inline-flex", alignItems: "center", gap: "0.3rem", padding: "0.2rem 0.65rem", borderRadius: "20px", background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.3)", color: "var(--danger)", cursor: "pointer", fontSize: "0.82rem", fontFamily: "var(--font-body)", marginTop: "0.4rem", userSelect: "none" },
  combinedBar: { display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.4rem", marginBottom: "1.25rem", padding: "0.4rem 0.75rem", background: "rgba(128,128,128,0.04)", border: "1px solid var(--border-color)", borderRadius: "12px" },
  divider: { width: "1px", height: "16px", background: "var(--border-color)", flexShrink: 0, margin: "0 0.1rem" },
  pillGroup: { display: "flex", alignItems: "center", gap: "0.15rem" },
  fileTag: { display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.79rem", color: "var(--text-secondary)", paddingRight: "0.25rem" },
  dropZone: { border: "2px dashed var(--border-color)", borderRadius: "16px", padding: "3.5rem 2rem", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", transition: "all 0.2s", background: "rgba(128,128,128,0.03)", marginBottom: "1.25rem" },
  dropActive: { borderColor: "var(--accent-primary)", background: "rgba(59,130,246,0.06)", boxShadow: "0 0 0 4px var(--accent-glow)" },
  dropContent: { display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", pointerEvents: "none" },
  dropTitle: { fontSize: "1.1rem", fontWeight: "600", color: "var(--text-primary)", marginTop: "0.5rem" },
  dropSub: { fontSize: "0.9rem", color: "var(--text-secondary)" },
  badges: { display: "flex", gap: "0.5rem", marginTop: "1rem", flexWrap: "wrap", justifyContent: "center" },
  badge: { padding: "0.25rem 0.65rem", borderRadius: "20px", background: "rgba(59,130,246,0.1)", color: "var(--accent-primary)", fontSize: "0.78rem", fontWeight: "600", letterSpacing: "0.04em", border: "1px solid rgba(59,130,246,0.2)" },
  errorBox: { display: "flex", alignItems: "flex-start", gap: "0.75rem", padding: "1rem 1.25rem", marginBottom: "1rem", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: "10px", color: "var(--danger)", fontSize: "0.9rem" },
  hintBox: { display: "flex", gap: "0.75rem", padding: "1rem 1.25rem", background: "rgba(128,128,128,0.05)", border: "1px solid var(--border-color)", borderRadius: "10px", color: "var(--text-secondary)", fontSize: "0.88rem", lineHeight: 1.7 },
  code: { background: "rgba(128,128,128,0.12)", padding: "1px 6px", borderRadius: "4px", fontFamily: "monospace", fontSize: "0.82rem", color: "var(--text-primary)", margin: "0 2px" },
  spinner: { width: "48px", height: "48px", border: "4px solid rgba(59,130,246,0.15)", borderTopColor: "var(--accent-primary)", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
  apiForm: { display: "flex", flexDirection: "column", gap: "1.25rem", padding: "2rem", background: "rgba(128,128,128,0.03)", borderRadius: "16px", border: "1px solid var(--border-color)", marginBottom: "1.25rem" },
  formGroup: { display: "flex", flexDirection: "column", gap: "0.5rem" },
  label: { fontSize: "0.85rem", fontWeight: "600", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" },
  input: { padding: "0.8rem 1rem", borderRadius: "8px", background: "rgba(128,128,128,0.05)", border: "1px solid var(--border-color)", color: "var(--text-primary)", fontSize: "1rem", fontFamily: "var(--font-body)", outline: "none", transition: "border-color 0.2s" },
  submitBtn: { display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", padding: "0.9rem", borderRadius: "8px", background: "var(--accent-primary)", color: "#fff", border: "none", fontSize: "1rem", fontWeight: "600", cursor: "pointer", marginTop: "1rem", transition: "all 0.2s" },
  strategySection: { marginBottom: "1.5rem" },
  sectionHeader: { display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.5rem" },
  sectionTitle: { fontSize: "1.2rem", fontWeight: "800", color: "#3b82f6", textTransform: "uppercase", letterSpacing: "0.08em", borderBottom: "2px solid #3b82f6", paddingBottom: "0.4rem" },
  strategyActionRow: { display: "flex", gap: "1.25rem", flexWrap: "wrap", marginBottom: "1.25rem" },
  settingsPanel: { display: "flex", flexDirection: "column", gap: "1.5rem", marginBottom: "2rem" },
  settingsGroup: { display: "flex", flexDirection: "column", gap: "1rem" },
  groupLabel: { fontSize: "0.85rem", fontWeight: "800", color: "#3b82f6", textTransform: "uppercase", letterSpacing: "0.1em", borderBottom: "2px solid #3b82f6", paddingBottom: "0.25rem", width: "fit-content", marginBottom: "0.5rem" },
  settingItem: { display: "flex", flexDirection: "column", gap: "0.4rem" },
  settingsDivider: { height: "1px", background: "#000000", opacity: 0.8, margin: "1rem 0" },
  statusArea: { display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.75rem 1rem", background: "rgba(128,128,128,0.05)", borderRadius: "8px", border: "1px solid var(--border-color)", color: "var(--text-primary)", fontSize: "0.85rem", fontFamily: "monospace" },
  statusText: { flex: 1, color: "var(--text-primary)" },
  infoPage: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "var(--bg-main)", zIndex: 999999, overflowY: "auto", animation: "pageSlideIn 0.4s cubic-bezier(0, 0, 0.2, 1)" },
  infoPageContent: { maxWidth: "1200px", margin: "0 auto", padding: "4rem 2rem" },
  infoPageHeader: { marginBottom: "3rem" },
  infoPageBody: {},
  backBtn: { display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--accent-primary)", fontWeight: "600", cursor: "pointer", marginBottom: "2rem", width: "fit-content", transition: "transform 0.2s" },
  infoPageTitleRow: { display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.5rem" },
  infoPageTitle: { fontSize: "2.5rem", fontWeight: "800", margin: 0, letterSpacing: "-0.02em" },
  infoPageSub: { color: "var(--text-secondary)", fontSize: "1.1rem", maxWidth: "600px" },
  infoGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "2rem" },
  infoCard: { background: "rgba(128,128,128,0.03)", border: "1px solid var(--border-color)", borderRadius: "24px", padding: "2rem", display: "flex", flexDirection: "column", gap: "1rem" },
  infoCardIcon: { color: "var(--accent-primary)", opacity: 0.8 },
  infoCardTitle: { fontSize: "1.2rem", fontWeight: "700", color: "var(--text-primary)" },
  infoCardDesc: { fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: 1.7 },
  radioLabel: { display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", padding: "0.5rem 1rem", borderRadius: "10px", background: "rgba(128,128,128,0.08)", border: "1px solid var(--border-color)", transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)", userSelect: "none" },
  radioLabelActive: { background: "rgba(59, 130, 246, 0.2)", borderColor: "var(--accent-primary)", boxShadow: "0 4px 12px rgba(59, 130, 246, 0.15)" },
  radioHidden: { display: "none" },
  radioText: { fontSize: "0.85rem", color: "var(--text-primary)", fontWeight: "600", transition: "all 0.2s" },
  radioTextActive: { color: "var(--accent-primary)", fontWeight: "800" },

  // Hero Section
  heroContainer: { flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "4rem 2rem", background: "radial-gradient(circle at top, rgba(59,130,246,0.05) 0%, transparent 70%)" },
  heroGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "2rem", maxWidth: "1200px", width: "100%", marginBottom: "4rem" },
  heroCard: { background: "var(--bg-panel)", border: "1px solid var(--border-color)", borderRadius: "12px", padding: "2.5rem", display: "flex", flexDirection: "column", gap: "1.5rem", position: "relative", overflow: "hidden", transition: "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)", boxShadow: "0 4px 24px rgba(0,0,0,0.2)" },
  heroCardTopBar: { position: "absolute", top: 0, left: 0, right: 0, height: "6px" },
  heroCardNumber: { background: "rgba(30,41,59,0.9)", color: "#fff", width: "48px", height: "48px", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", fontWeight: "800", fontFamily: "var(--font-display)", marginBottom: "0.5rem" },
  heroCardTitle: { fontSize: "1.75rem", fontWeight: "800", color: "var(--text-primary)", letterSpacing: "0.05em", textTransform: "uppercase", margin: 0 },
  heroCardSub: { fontSize: "1.1rem", fontWeight: "700", color: "var(--text-primary)", marginBottom: "0.5rem", display: "block" },
  heroCardDivider: { width: "80px", height: "4px", background: "#f59e0b", marginBottom: "1.5rem" },
  heroCardDesc: { fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: 1.7, margin: 0 },

  heroFooter: { width: "100%", background: "rgba(30,41,59,0.9)", padding: "1rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "1.5rem", borderTop: "1px solid rgba(255,255,255,0.1)", position: "absolute", bottom: 0, left: 0 },
  heroFooterText: { color: "#fff", fontSize: "0.9rem", fontWeight: "600", display: "flex", alignItems: "center", gap: "0.75rem", opacity: 0.9 },
  heroFooterArrow: { color: "rgba(255,255,255,0.4)" },
  bandCell:          { padding: "1rem", borderBottom: "1px solid #e2e8f0", fontSize: "1.1rem" },

  // Dual Cell Upload
  uploadGrid:        { display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.5rem" },
  uploadCell:        { background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-color)", borderRadius: "8px", padding: "1rem", display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", cursor: "pointer", transition: "all 0.3s ease", textAlign: "left" },
  trainCell:         { borderLeft: "4px solid #1e293b" },
  testCell:          { borderLeft: "4px solid #f59e0b" },
  cellInfo:          { display: "flex", flexDirection: "column", flex: 1, gap: "0.25rem" },
  cellTitle:         { fontSize: "0.75rem", fontWeight: "800", color: "#f59e0b", letterSpacing: "0.05em", textTransform: "uppercase" },
  cellDataYear:      { fontSize: "1.1rem", fontWeight: "900", color: "#fff" },
  cellDesc:          { fontSize: "0.65rem", color: "var(--text-secondary)", fontStyle: "italic", lineHeight: "1.1" },
  warningBox:        { background: "rgba(245, 158, 11, 0.05)", border: "1px solid rgba(245, 158, 11, 0.2)", borderRadius: "6px", padding: "0.75rem", color: "#f59e0b", fontSize: "0.7rem", display: "flex", alignItems: "start", gap: "0.5rem", marginTop: "1rem" },
  quickPathBtn:      { background: "rgba(30,41,59,1)", border: "1px solid rgba(255,255,255,0.1)", color: "#fff", padding: "0.4rem 0.75rem", borderRadius: "4px", fontSize: "0.65rem", cursor: "pointer", transition: "all 0.2s", whiteSpace: "nowrap" },
};

export const css = `
  .src-card:hover {
    border-color: var(--accent-primary) !important;
    background: rgba(59,130,246,0.06) !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(59,130,246,0.12);
  }
  .icon-pill:hover {
    background: rgba(128,128,128,0.14) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-focus) !important;
  }
  .ctrl-pill {
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    font-family: var(--font-body);
    cursor: pointer;
    user-select: none;
    color: var(--text-secondary);
    transition: all 0.13s ease;
    border: 1px solid transparent;
  }
  .ctrl-pill:hover { background: rgba(128,128,128,0.1); color: var(--text-primary); }
  .ctrl-pill-active {
    background: var(--accent-primary);
    color: #fff !important;
    border-color: var(--accent-primary) !important;
    box-shadow: 0 2px 8px var(--accent-glow);
  }
  .ctrl-pill-all {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 22px;
    padding: 0;
    background: rgba(128,128,128,0.08);
  }
  .ctrl-pill-all:hover { background: rgba(128,128,128,0.1); color: var(--text-primary); }
  .submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--accent-glow);
    filter: brightness(1.1);
  }
  .submit-btn:active:not(:disabled) { transform: translateY(0); }
  .radio-chip:hover {
    background: rgba(128,128,128,0.15) !important;
    border-color: var(--accent-primary) !important;
    transform: translateY(-1px);
  }
  button:disabled { opacity: 0.5 !important; cursor: not-allowed !important; filter: grayscale(0.5); }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .ai-pill {
    display: flex; align-items: center; gap: 0.35rem;
    color: var(--accent-primary);
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
  }
  .ai-pill:hover { background: var(--accent-primary) !important; color: #fff !important; }
  .modern-btn {
    padding: 0.8rem 1.8rem; font-size: 1rem; border-radius: 14px;
    display: flex; align-items: center; gap: 0.8rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 700; cursor: pointer; user-select: none;
    background: linear-gradient(135deg, #3b82f6 0%, #0891b2 100%);
    color: #ffffff !important; border: none;
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.35);
  }
  .modern-btn:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 15px 35px rgba(59, 130, 246, 0.5); filter: brightness(1.1); }
  .modern-btn:active { transform: translateY(-1px) scale(0.98); }
  .modern-btn.ctrl-pill-disabled { background: #4a5568 !important; opacity: 0.5; cursor: not-allowed; box-shadow: none; transform: none !important; }
  input:focus, select:focus { border-color: var(--accent-primary) !important; }
  .submit-btn:hover { background: var(--accent-hover) !important; box-shadow: 0 4px 14px var(--accent-glow); transform: translateY(-1px); }
  .spin { animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
  @keyframes pageSlideIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
  .modern-select-container { position: relative; width: 100%; }
  .modern-select-trigger {
    padding: 0.8rem 1.25rem; background: rgba(30,41,59,0.5);
    border: 1px solid rgba(255,255,255,0.12); border-radius: 14px;
    color: #f8fafc; font-weight: 500; cursor: pointer;
    display: flex; align-items: center; justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }
  .modern-select-trigger:hover, .modern-select-trigger.active { background: rgba(51,65,85,0.6); border-color: var(--accent-primary); }
  .modern-select-trigger .arrow { transition: transform 0.3s ease; color: var(--accent-primary); }
  .modern-select-trigger .arrow.open { transform: rotate(180deg); }
  .modern-select-dropdown {
    position: absolute; top: calc(100% + 8px); left: 0; right: 0;
    background: rgba(15,23,42,0.95); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.15); border-radius: 14px;
    overflow: hidden; z-index: 1000;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    animation: dropdownIn 0.2s ease-out;
  }
  @keyframes dropdownIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
  .modern-select-option { padding: 0.8rem 1.25rem; color: #cbd5e1; cursor: pointer; transition: all 0.2s; }
  .modern-select-option:hover { background: rgba(59,130,246,0.15); color: white; padding-left: 1.5rem; }
  .modern-select-option.selected { color: var(--accent-primary); font-weight: 600; background: rgba(59,130,246,0.05); }
  
  .hero-card:hover {
    transform: translateY(-8px);
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
  }
  .hero-card:hover .hero-divider {
    width: 120px !important;
    background: #3b82f6 !important;
  }
`;
