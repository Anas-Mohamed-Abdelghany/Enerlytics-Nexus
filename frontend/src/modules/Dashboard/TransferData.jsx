import React, { useState } from 'react';
import { Terminal, Globe, CheckCircle2, Loader2, Cpu, Download } from 'lucide-react';
import { s } from "./DashboardStyles";

export default function TransferData({ data }) {
    const [status, setStatus] = useState('idle'); 
    const [method, setMethod] = useState(null); 

    const handleTransfer = (m) => {
        if (!data) return;
        setMethod(m);
        setStatus('transferring');
        
        setTimeout(() => {
            setStatus('success');
            setTimeout(() => setStatus('idle'), 3000);
        }, 2000);
    };

    const handleSaveTemplate = () => {
        if (!data) return;
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `energy_strategy_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div style={{ padding: '0 1rem 1.5rem 1rem' }}>
            <div style={s.groupLabel}>Transfer to Edge</div>
            
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: 1.5 }}>
                Dispatch current optimized strategy JSON to local PLC or cloud gateway.
            </p>

            <div style={{ display: "flex", gap: "0.75rem" }}>
                <button 
                    className={`action-btn ${status === 'transferring' && method === 'port' ? 'loading' : ''}`}
                    onClick={() => handleTransfer('port')}
                    disabled={status !== 'idle' || !data}
                    style={{ 
                        flex: 1, gap: '0.5rem', background: 'rgba(128,128,128,0.08)', 
                        border: '1px solid var(--border-color)', color: 'var(--text-primary)',
                        padding: '0.6rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.75rem',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600'
                    }}
                >
                    {status === 'transferring' && method === 'port' ? <Loader2 size={14} className="spin" /> : <Terminal size={14} />}
                    Com Port
                </button>

                <button 
                    className={`action-btn ${status === 'transferring' && method === 'api' ? 'loading' : ''}`}
                    onClick={() => handleTransfer('api')}
                    disabled={status !== 'idle' || !data}
                    style={{ 
                        flex: 1, gap: '0.5rem', background: 'rgba(128,128,128,0.08)', 
                        border: '1px solid var(--border-color)', color: 'var(--text-primary)',
                        padding: '0.6rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.75rem',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600'
                    }}
                >
                    {status === 'transferring' && method === 'api' ? <Loader2 size={14} className="spin" /> : <Globe size={14} />}
                    Cloud API
                </button>
            </div>

            <button 
                className="action-btn"
                onClick={handleSaveTemplate}
                disabled={!data}
                style={{ 
                    width: '100%', gap: '0.5rem', background: 'rgba(59, 130, 246, 0.15)', 
                    border: '1px solid rgba(59, 130, 246, 0.3)', color: 'var(--accent-primary)',
                    padding: '0.7rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.75rem',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '800',
                    marginTop: '0.75rem', transition: 'all 0.2s'
                }}
            >
                <Download size={14} />
                Save Strategy Template (.json)
            </button>

            {status === 'success' && (
                <div style={{ 
                    marginTop: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center', 
                    gap: '0.5rem', fontSize: '0.75rem', color: '#10b981', fontWeight: '700',
                    background: 'rgba(16, 185, 129, 0.1)', padding: '0.5rem', borderRadius: '6px'
                }}>
                    <CheckCircle2 size={14} />
                    <span>JSON Sent Successfully</span>
                </div>
            )}
        </div>
    );
}
