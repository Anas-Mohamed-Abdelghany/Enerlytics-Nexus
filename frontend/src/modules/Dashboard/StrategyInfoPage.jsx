import React from "react";
import { Brain, ChevronLeft, Activity, Target, TrendingUp, Calendar, Clock, RotateCcw, Maximize2, TrendingDown, Zap } from "lucide-react";
import { s } from "./DashboardStyles";

export default function StrategyInfoPage({ setShowStrategyInfo }) {
  return (
    <div style={s.infoPage}>
      <div style={s.infoPageContent}>
        <div style={s.infoPageHeader}>
          <div style={s.backBtn} onClick={() => setShowStrategyInfo(false)}>
            <ChevronLeft size={20} />
            <span>Return to Dashboard</span>
          </div>
          <div style={s.infoPageTitleRow}>
            <Brain size={32} color="var(--accent-primary)" />
            <h1 style={s.infoPageTitle}>Strategy Intelligence Hub</h1>
          </div>
          <p style={s.infoPageSub}>Deep insights into the algorithmic models powering Enerlytics AI</p>
        </div>

        <div style={s.infoPageBody}>
          <div style={s.infoGrid}>
            {[
              { name: "Marubozu", icon: <Zap />, desc: "Identifies candles with no shadows, indicating extreme buying or selling pressure. A bullish Marubozu suggests continued upward momentum, while a bearish one signals strong selling interest." },
              { name: "Price Action", icon: <Activity />, desc: "Focuses on raw price movements and candlestick geometry. It identifies key transition patterns like Dojis and Haramis to predict market reversals before indicators react." },
              { name: "Range Trading", icon: <Target />, desc: "Calculates dynamic support and resistance levels using 20-period rolling high/low data. Perfect for sideways markets where price oscillates between established boundaries." },
              { name: "Trend Trading", icon: <TrendingUp />, desc: "Uses 50-day and 200-day Moving Averages to identify the macro market direction. Signals entries based on 'Golden Cross' (bullish) and 'Death Cross' (bearish) events." },
              { name: "Position Trading", icon: <Calendar />, desc: "A long-term trend-following model based on the 100-day Moving Average. Designed for investors holding positions over months rather than days." },
              { name: "Day Trading", icon: <Clock />, desc: "Analyzes intraday volatility and range expansion. It identifies high-probability setups that resolve within a single trading session based on daily range averages." },
              { name: "Scalping", icon: <Zap />, desc: "High-frequency precision model targeting micro-movements of less than 0.2%. It relies on rapid execution and identifying extreme short-term order flow imbalances." },
              { name: "Swing Trading", icon: <RotateCcw />, desc: "Focuses on 'swings' in the market over 5 to 10 days. It identifies cyclic local highs and lows to capture the meat of a medium-term trend move." },
              { name: "Breakout Trading", icon: <Maximize2 />, desc: "Detects structural breaks through 20-day price channels. It triggers when price closes decisively outside a consolidated range, signaling the start of a new trend." },
              { name: "Retracement Trading", icon: <TrendingDown />, desc: "Calculates pullback percentages in established trends. It identifies 'buy the dip' or 'sell the rip' opportunities when price temporarily moves against the trend." },
              { name: "Momentum Trading", icon: <Zap />, desc: "Measures the velocity of price changes using a 5-day rate-of-change engine. It identifies assets that are accelerating in a specific direction with increasing volume support." },
              { name: "MACD Trading", icon: <Activity />, desc: "Uses the Moving Average Convergence Divergence oscillator. It tracks the relationship between two moving averages to identify changes in strength, direction, and momentum." },
            ].map(strat => (
              <div key={strat.name} style={s.infoCard}>
                <div style={s.infoCardIcon}>{strat.icon}</div>
                <div style={s.infoCardTitle}>{strat.name}</div>
                <div style={s.infoCardDesc}>{strat.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
