import React, { useState } from "react";
import useDashboard from "./useDashboard";
import { s, css } from "./DashboardStyles";
import {
    Upload, Wifi, Settings, BrainCircuit, Activity,
    Database, BarChart3, ChevronLeft, ChevronRight,
    Target, Zap, TrendingUp, MoveRight
} from 'lucide-react';

// Sub-components
import ApiForm from "./ApiForm";
import UploadView from "./UploadView";
import BatteryDashboard from "./BatteryDashboard";
import AIStrategyHub from "./AIStrategyHub";
import ChartToolbar from "./TradingChart/ChartToolbar";
import AIIntelligenceReports from "./AIIntelligenceReports";
import TransferData from "./TransferData";

/**
 * Main Energy Dashboard Orchestrator
 * Integrates data sources and AI controls directly into the Battery EMS theme.
 */
export default function Dashboard({ isDarkMode }) {
    const dashboard = useDashboard(isDarkMode);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [configTab, setConfigTab] = useState("source"); // 'source' or 'ai'

    const {
        // Core
        mode, setMode, fullSeries, chartData, uploading,

        // AI State
        predictionResult, predicting, analyzing, statusMessage,
        predictionType, setPredictionType,
        predictionHorizon, setPredictionHorizon,
        trainingWindow, setTrainingWindow,
        architecture, setArchitecture,
        aprilSource, setAprilSource,
        septSource, setSeptSource,
        checkSamples, setCheckSamples,
        selectedStrategies, setSelectedStrategies,
        isBatteryDemo,

        // Plotly / Visualization
        plotlyHtml, loadingChart,
        handleChartTypeChange, handleAddMainIndicator, handleAddSubIndicator,
        activeIndicators, activeOscillators,

        // UI / Details
        setShowStrategyInfo,
        showValidationDetails, setShowValidationDetails,
        showRobustnessDetails, setShowRobustnessDetails,

        // Handlers
        handlePredict, handleStrategy, handleDownloadCSV,
        handleTrainAll,
        changeTimeframe, changeInterval, timeframe, interval,
        handleManualOptimize
    } = dashboard;

    // Auto-switch to AI tab when data is loaded
    React.useEffect(() => {
        if (chartData.length > 0 && configTab === "source" && !predicting) {
            setConfigTab("ai");
        }
    }, [chartData.length]);

    // Helper to generate the 24x7 matrix for the heatmap (Mon-Sun x 0-23h)
    const priceMatrix = React.useMemo(() => {
        const matrix = Array(7).fill(0).map(() => Array(24).fill(0));
        const counts = Array(7).fill(0).map(() => Array(24).fill(0));
        if (!chartData.length) return matrix;

        chartData.forEach(d => {
            const dt = new Date(d.timestamp);
            const hour = dt.getHours();
            const dow = (dt.getDay() + 6) % 7; // 0=Mon, ..., 6=Sun
            if (hour >= 0 && hour < 24 && dow >= 0 && dow < 7) {
                matrix[dow][hour] += (d.close || 0);
                counts[dow][hour] += 1;
            }
        });

        return matrix.map((row, i) => row.map((sum, j) => counts[i][j] > 0 ? sum / counts[i][j] : 0));
    }, [chartData]);

    const hasEnergyData = React.useMemo(() => {
        return chartData.some(d => (d.battery_p != null) || (d.grid_p != null) || (d.load_p != null) || (d.pv_p != null));
    }, [chartData]);

    // Theme-aware styles
    const themeStyles = {
        appWrapper: {
            display: 'flex',
            height: 'calc(100vh - 70px)',
            width: '100vw',
            background: 'var(--bg-main)',
            overflow: 'hidden',
            fontFamily: 'var(--font-body)',
            color: 'var(--text-primary)'
        },
        sidebar: {
            width: sidebarOpen ? '320px' : '0',
            background: 'var(--bg-panel)',
            borderRight: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            position: 'relative',
            zIndex: 100,
            overflowX: 'hidden',
            overflowY: 'auto'
        },
        sidebarHeader: {
            padding: '1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid var(--border-color)'
        },
        brand: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontWeight: '700',
            fontSize: '1.1rem',
            color: 'var(--text-primary)'
        },
        closeBtn: {
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer'
        },
        openBtn: {
            position: 'absolute',
            top: '1.5rem',
            left: '1.5rem',
            zIndex: 99,
            background: 'var(--accent-primary)',
            color: '#fff',
            border: 'none',
            padding: '0.75rem',
            borderRadius: '12px',
            cursor: 'pointer',
            boxShadow: '0 4px 15px var(--accent-glow)'
        },
        tabHeader: {
            display: 'flex',
            padding: '1rem',
            gap: '0.5rem',
            background: 'var(--bg-panel)',
            opacity: 0.9
        },
        tabBtn: {
            flex: 1,
            padding: '0.6rem',
            borderRadius: '8px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            fontSize: '0.8rem',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            cursor: 'pointer',
            transition: '0.2s'
        },
        tabBtnActive: {
            background: 'rgba(128,128,128,0.1)',
            color: 'var(--accent-primary)',
            border: '1px solid var(--border-color)'
        },
        sidebarContent: {
            flex: 1,
            overflowY: 'auto',
            padding: '1.5rem'
        },
        modeToggle: {
            display: 'flex',
            background: 'rgba(128,128,128,0.05)',
            padding: '0.25rem',
            borderRadius: '10px',
            marginBottom: '1.5rem',
            border: '1px solid var(--border-color)'
        },
        modeBtn: {
            flex: 1,
            padding: '0.5rem',
            borderRadius: '8px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            fontSize: '0.75rem',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem'
        },
        modeBtnActive: {
            background: 'var(--bg-panel)',
            color: 'var(--text-primary)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid var(--border-color)'
        },
        emptySource: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '200px',
            color: 'var(--text-secondary)',
            textAlign: 'center',
            gap: '1rem',
            fontSize: '0.85rem'
        },
        uploadOverlay: {
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'var(--bg-panel)',
            opacity: 0.95,
            backdropFilter: 'blur(4px)',
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem',
            color: 'var(--text-primary)',
            fontSize: '0.9rem'
        },
        mainArea: {
            flex: 1,
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            background: 'var(--bg-main)',
            minWidth: 0
        },
        dashboardContainer: {
            flex: 1,
            padding: 0,
            overflowY: 'auto',
            background: 'var(--bg-main)',
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0
        },
        placeholderView: {
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem'
        },
        heroEmpty: {
            textAlign: 'center',
            maxWidth: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1.5rem'
        },
        badgeRow: {
            display: 'flex',
            gap: '0.75rem',
            marginTop: '1rem'
        },
        demoBadge: {
            fontSize: '0.7rem',
            padding: '0.4rem 0.8rem',
            background: 'rgba(128,128,128,0.05)',
            borderRadius: '20px',
            color: 'var(--text-secondary)',
            border: '1px solid var(--border-color)'
        }
    };

    return (
        <div style={themeStyles.appWrapper}>
            {/* ── Sidebar: Control Center ── */}
            <aside style={{ ...themeStyles.sidebar, width: sidebarOpen ? '380px' : '0px', opacity: sidebarOpen ? 1 : 0 }}>
                <div style={themeStyles.sidebarHeader}>
                    <div style={themeStyles.brand}>
                        <Activity color="var(--accent-primary)" size={24} />
                        <span>BESS Control Center</span>
                    </div>
                    <button style={themeStyles.closeBtn} onClick={() => setSidebarOpen(false)}>
                        <ChevronLeft size={20} />
                    </button>
                </div>

                <div style={themeStyles.tabHeader}>
                    <button
                        style={{ ...themeStyles.tabBtn, ...(configTab === 'source' ? themeStyles.tabBtnActive : {}) }}
                        onClick={() => setConfigTab('source')}
                    >
                        <Database size={16} /> Data Source
                    </button>
                    <button
                        style={{ ...themeStyles.tabBtn, ...(configTab === 'ai' ? themeStyles.tabBtnActive : {}) }}
                        onClick={() => setConfigTab('ai')}
                    >
                        <BrainCircuit size={16} /> AI Strategy
                    </button>
                </div>

                <div style={themeStyles.sidebarContent}>
                    {configTab === 'source' ? (
                        <div style={themeStyles.sourceControl}>
                            <div style={themeStyles.modeToggle}>
                                <button
                                    style={{ ...themeStyles.modeBtn, ...(mode === 'upload' ? themeStyles.modeBtnActive : {}) }}
                                    onClick={() => setMode('upload')}
                                >
                                    <Upload size={16} /> CSV
                                </button>
                                <button
                                    style={{ ...themeStyles.modeBtn, ...(mode === 'api' ? themeStyles.modeBtnActive : {}) }}
                                    onClick={() => setMode('api')}
                                >
                                    <Wifi size={16} /> API
                                </button>
                            </div>

                            {mode === 'upload' && (
                                <UploadView
                                    {...dashboard}
                                    isBatteryDemo={isBatteryDemo}
                                    trainFileRef={dashboard.trainFileRef}
                                    testFileRef={dashboard.testFileRef}
                                    onUploadTrain={dashboard.handleTrainFile}
                                    onUploadTest={dashboard.handleTestFile}
                                    onUseSavedTrain={dashboard.handleUseSavedTrain}
                                    loadingTrain={dashboard.loadingTrain}
                                    loadingTest={dashboard.loadingTest}
                                    error={dashboard.error}
                                />
                            )}
                            {mode === 'api' && <ApiForm {...dashboard} />}
                            {!mode && (
                                <div style={themeStyles.emptySource}>
                                    <Database size={40} opacity={0.2} />
                                    <p>Select a data source to begin optimization</p>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div style={themeStyles.aiControl}>
                            <AIStrategyHub
                                fullSeries={fullSeries}
                                chartData={chartData}
                                predicting={predicting}
                                analyzing={analyzing}
                                predictionResult={predictionResult}
                                statusMessage={statusMessage}
                                predictionType={predictionType}
                                setPredictionType={setPredictionType}
                                predictionHorizon={predictionHorizon}
                                setPredictionHorizon={setPredictionHorizon}
                                trainingWindow={trainingWindow}
                                setTrainingWindow={setTrainingWindow}
                                architecture={architecture}
                                setArchitecture={setArchitecture}
                                aprilSource={aprilSource}
                                setAprilSource={setAprilSource}
                                septSource={septSource}
                                setSeptSource={setSeptSource}
                                checkSamples={checkSamples}
                                setCheckSamples={setCheckSamples}
                                selectedStrategies={selectedStrategies}
                                setSelectedStrategies={setSelectedStrategies}
                                setShowStrategyInfo={setShowStrategyInfo}
                                showValidationDetails={showValidationDetails}
                                setShowValidationDetails={setShowValidationDetails}
                                showRobustnessDetails={showRobustnessDetails}
                                setShowRobustnessDetails={setShowRobustnessDetails}
                                handlePredict={handlePredict}
                                handleStrategy={handleStrategy}
                                handleTrainAll={handleTrainAll}
                                handleDownloadCSV={handleDownloadCSV}
                            />
                        </div>
                    )}
                    {chartData.length > 0 && (
                        <>
                            <div style={s.settingsDivider} />
                            <TransferData data={predictionResult || chartData} />
                        </>
                    )}
                </div>

                {uploading && (
                    <div style={themeStyles.uploadOverlay}>
                        <div style={s.spinner} />
                        <span>Processing Energy Data...</span>
                    </div>
                )}
            </aside>

            {/* ── Main Dashboard Area ── */}
            <main style={themeStyles.mainArea}>
                {!sidebarOpen && (
                    <button style={themeStyles.openBtn} onClick={() => setSidebarOpen(true)}>
                        <Settings size={20} />
                    </button>
                )}

                <div style={themeStyles.dashboardContainer}>
                    {/* 1. Main Data Plot Box */}
                    {chartData.length > 0 ? (
                        <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div className="main-panel" style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '20px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <Activity size={20} color="#3b82f6" />
                                        <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                                            {predictionResult ? "AI Market Strategy & Forecasting" : "Historical Market Data Analysis"}
                                        </h3>
                                    </div>
                                    <ChartToolbar
                                        onChartTypeChange={handleChartTypeChange}
                                        onAddMainIndicator={handleAddMainIndicator}
                                        onAddSubIndicator={handleAddSubIndicator}
                                        onStartDrawing={() => { }}
                                        onClearDrawings={() => { }}
                                        activeIndicators={activeIndicators}
                                        activeOscillators={activeOscillators}
                                        timeframe={timeframe}
                                        interval={interval}
                                        onTimeframeChange={changeTimeframe}
                                        onIntervalChange={changeInterval}
                                    />
                                </div>

                                <div style={{ height: '500px', width: '100%', position: 'relative' }}>
                                    {plotlyHtml && (
                                        <iframe
                                            srcDoc={typeof plotlyHtml === 'string' ? plotlyHtml : (plotlyHtml.main || plotlyHtml.forecast)}
                                            style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
                                            title="Main Price Chart"
                                        />
                                    )}
                                    {loadingChart && (
                                        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                                            <div className="spin" style={{ width: '32px', height: '32px', border: '3px solid rgba(59,130,246,0.3)', borderTopColor: '#3b82f6', borderRadius: '50%' }} />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                            <div className="mission-container" style={{ padding: '3rem', maxWidth: '1200px', margin: '0 auto' }}>
                                <div className="mission-layout" style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '4rem', alignItems: 'start' }}>
                                    <div className="mission-text">
                                        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '2rem', color: 'var(--text-primary)' }}>Your Mission</h1>
                                        <p style={{ fontSize: '1.1rem', lineHeight: 1.6, color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                                            You are given a residential site in Italy connected to the utility grid, a <strong>9 kWp</strong> rooftop solar PV system, and a <strong>16 kWh</strong> lithium battery.
                                        </p>
                                        <div className="objectives" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '3rem' }}>
                                            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Build two things:</h3>
                                            <div style={{ display: 'flex', alignItems: 'start', gap: '1rem' }}>
                                                <div style={{ width: '24px', height: '24px', background: '#f59e0b', borderRadius: '4px', flexShrink: 0, marginTop: '4px' }} />
                                                <div>
                                                    <strong style={{ display: 'block', fontSize: '1.1rem' }}>A load forecasting model</strong>
                                                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontStyle: 'italic' }}>trained on 2024 data, applied to 2025</span>
                                                </div>
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'start', gap: '1rem' }}>
                                                <div style={{ width: '24px', height: '24px', background: '#f59e0b', borderRadius: '4px', flexShrink: 0, marginTop: '4px' }} />
                                                <div>
                                                    <strong style={{ display: 'block', fontSize: '1.1rem' }}>A rolling-horizon battery</strong>
                                                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontStyle: 'italic' }}>dispatch controller that cuts the electricity bill</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="sign-convention">
                                            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Power Sign Convention</h3>
                                            <table style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '8px', overflow: 'hidden' }}>
                                                <thead>
                                                    <tr style={{ background: '#1e293b', color: '#fff', textAlign: 'left' }}>
                                                        <th style={{ padding: '12px 16px' }}>Variable / Sign</th>
                                                        <th style={{ padding: '12px 16px' }}>Meaning</th>
                                                    </tr>
                                                </thead>
                                                <tbody style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)' }}>
                                                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                        <td className="mono" style={{ padding: '10px 16px' }}>P_battery &lt; 0</td>
                                                        <td style={{ padding: '10px 16px' }}>Battery charging</td>
                                                    </tr>
                                                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                        <td className="mono" style={{ padding: '10px 16px' }}>P_battery &gt; 0</td>
                                                        <td style={{ padding: '10px 16px' }}>Battery discharging</td>
                                                    </tr>
                                                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                        <td className="mono" style={{ padding: '10px 16px' }}>P_grid &gt; 0</td>
                                                        <td style={{ padding: '10px 16px' }}>Importing from grid</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="mono" style={{ padding: '10px 16px' }}>P_grid &lt; 0</td>
                                                        <td style={{ padding: '10px 16px' }}>Exporting to grid</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    <div className="site-layout-panel" style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '24px', padding: '2rem', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
                                        <h2 style={{ textAlign: 'center', fontSize: '1.2rem', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2rem', letterSpacing: '1px' }}>Site Layout</h2>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            <div style={{ background: '#f59e0b', padding: '1.5rem', borderRadius: '12px', textAlign: 'center', color: '#fff' }}>
                                                <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>Solar PV (9 kWp)</div>
                                            </div>
                                            <div style={{ background: '#3b82f6', padding: '1.5rem', borderRadius: '12px', textAlign: 'center', color: '#fff' }}>
                                                <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>Grid (6 kW limit)</div>
                                            </div>
                                            <div style={{ background: '#10b981', padding: '1.5rem', borderRadius: '12px', textAlign: 'center', color: '#fff' }}>
                                                <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>Battery (16 kWh / 8 kW)</div>
                                            </div>
                                            <div style={{ background: '#475569', padding: '1.5rem', borderRadius: '12px', textAlign: 'center', color: '#fff' }}>
                                                <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>Load (Must be served 100%)</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div style={{ background: '#1e293b', color: '#fff', padding: '1rem', textAlign: 'center', borderRadius: '8px', marginTop: '3rem', fontWeight: 600 }}>
                                    The site load must be fully served at every 15-minute interval without exception
                                </div>
                            </div>
                    )}

                    {/* 2. Battery Optimization Viewer / Competition Data Viewer */}
                    {(predictionResult?.optimizer || hasEnergyData) && (
                        <div style={{ borderTop: '1px solid var(--border-color)', flexShrink: 0, overflowX: 'hidden' }}>
                            <BatteryDashboard
                                optimizerResult={predictionResult?.optimizer}
                                forecastResult={predictionResult}
                                historicalData={hasEnergyData ? chartData : null}
                                priceHistory={{
                                    timestamps: predictionResult?.optimizer?.timestamps || chartData.map(d => d.timestamp),
                                    prices: predictionResult?.points?.map(p => p.forecast) || chartData.map(d => d.selling_price || d.close),
                                    hour_dow_matrix: priceMatrix
                                }}
                                isLoading={predicting}
                                timeframe={timeframe}
                                setTimeframe={changeTimeframe}
                                interval={interval}
                                setInterval={changeInterval}
                                architecture={architecture}
                                aprilSource={aprilSource}
                                septSource={septSource}
                                predictionType={predictionType}
                                onManualOptimize={handleManualOptimize}
                            />
                        </div>
                    )}

                    {/* Intelligence Reports Section (XAI, Validation, Robustness) */}
                    {predictionResult && (
                        <div style={{ padding: '2rem', borderTop: '1px solid var(--border-color)', background: 'var(--bg-panel)', flexShrink: 0 }}>
                            <AIIntelligenceReports
                                predictionResult={predictionResult}
                                predictionType={predictionType}
                                checkSamples={checkSamples}
                                showValidationDetails={showValidationDetails}
                                setShowValidationDetails={setShowValidationDetails}
                                showRobustnessDetails={showRobustnessDetails}
                                setShowRobustnessDetails={setShowRobustnessDetails}
                            />
                        </div>
                    )}
                </div>
            </main>

            <style>{css}</style>
        </div>
    );
}
