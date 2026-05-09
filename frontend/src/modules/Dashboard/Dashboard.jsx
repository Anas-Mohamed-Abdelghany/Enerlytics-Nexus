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
        changeTimeframe, changeInterval, timeframe, interval
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
                        <div style={s.heroContainer}>
                            <div style={s.heroGrid}>
                                {/* 01. PREDICT */}
                                <div className="hero-card" style={s.heroCard}>
                                    <div style={{ ...s.heroCardTopBar, background: '#1e293b' }} />
                                    <div style={s.heroCardNumber}>01</div>
                                    <div>
                                        <h2 style={s.heroCardTitle}>PREDICT</h2>
                                        <span style={s.heroCardSub}>Load Forecasting</span>
                                    </div>
                                    <div className="hero-divider" style={s.heroCardDivider} />
                                    <p style={s.heroCardDesc}>
                                        Deep learning models ingest historical consumption, solar generation, temperature, and price signals to forecast load at 15-minute resolution.
                                    </p>
                                </div>

                                {/* 02. OPTIMISE */}
                                <div className="hero-card" style={s.heroCard}>
                                    <div style={{ ...s.heroCardTopBar, background: '#3b82f6' }} />
                                    <div style={s.heroCardNumber}>02</div>
                                    <div>
                                        <h2 style={{ ...s.heroCardTitle, color: '#3b82f6' }}>OPTIMISE</h2>
                                        <span style={s.heroCardSub}>Battery Dispatch</span>
                                    </div>
                                    <div className="hero-divider" style={s.heroCardDivider} />
                                    <p style={s.heroCardDesc}>
                                        A rolling-horizon Model Predictive Controller solves the optimal charge/discharge schedule every step — buying cheap, selling expensive.
                                    </p>
                                </div>

                                {/* 03. EARN */}
                                <div className="hero-card" style={s.heroCard}>
                                    <div style={{ ...s.heroCardTopBar, background: '#10b981' }} />
                                    <div style={s.heroCardNumber}>03</div>
                                    <div>
                                        <h2 style={{ ...s.heroCardTitle, color: '#10b981' }}>EARN</h2>
                                        <span style={s.heroCardSub}>Maximised Savings</span>
                                    </div>
                                    <div className="hero-divider" style={s.heroCardDivider} />
                                    <p style={s.heroCardDesc}>
                                        The system automatically arbitrages time-of-use tariffs, exports surplus at peak prices, and supports grid emergencies for additional revenue.
                                    </p>
                                </div>
                            </div>

                            <div style={s.heroFooter}>
                                <div style={s.heroFooterText}>
                                    AI sends a signal <MoveRight size={16} className="heroFooterArrow" />
                                    Hardware communicates with all inverters <MoveRight size={16} className="heroFooterArrow" />
                                    Instant Response
                                </div>
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
