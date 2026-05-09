# ⚡ Enerlytics Nexus: BESS Arbitrage Optimizer

### *Next-Generation Battery Energy Storage System (BESS) Suite for the Solship Hackathon*

![Version](https://img.shields.io/badge/version-1.2.0--pivot-blueviolet)
![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20|%20React%20|%20LightGBM-green)
![Optimization](https://img.shields.io/badge/solver-SciPy%20HiGHS-orange)

Enerlytics Nexus is a high-fidelity **Battery Energy Storage System (BESS)** optimization and forecasting platform. Originally built as a market analytics tool, it has been technically pivoted into a specialized suite for maximizing revenue from behind-the-meter (BTM) storage assets in the Italian energy market.

---

## 🚀 Key Technical Pivots

### 1. Mathematical Optimization Engine
*   **LP Formulation**: Uses `scipy.optimize.linprog` with the **HiGHS** solver to minimize grid import costs.
*   **Vectorized Dynamics**: Implements NumPy-based vectorized constraint matrices for rapid 15-minute resolution scheduling across a 96-step horizon.
*   **Real-world Physics**: Models charge/discharge efficiency (95%), state-of-charge (SOC) bounds, and grid interconnection limits.

### 2. Advanced AI Forecaster
*   **LightGBM + MAPIE**: Transitioned from simple LSTMs to a gradient-boosted ensemble wrapped in **MAPIE** for distribution-free **Conformal Prediction Intervals**.
*   **Exogenous Features**: Integrated **Astral** solar tracking (Sunrise/Sunset logic for Milan) and Italian public holiday calendars to capture complex energy seasonality.
*   **Horizon Sensitivity**: Forensic analysis of prediction decay over time (4h to 48h windows).

### 3. Explainable AI (XAI)
*   **SHAP Waterfall Plots**: Moving beyond correlation to forensic feature contribution analysis.
*   **Local Interpretability**: Provides clear "reasoning" for every 15-minute price shift, increasing institutional trust.

### 4. High-Fidelity Visualization
*   **Plotly.js Suite**: Interactive 3-panel system timelines (Price, Energy, SOC).
*   **Live Replay Engine**: Animated playback of the optimized battery schedule.
*   **ROI Heatmaps**: Visual mapping of historical "Charge Cheap" windows.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, NumPy, SciPy (HiGHS), LightGBM, MAPIE, SHAP.
- **Frontend**: React 18, Vite, Plotly.js, Lucide Icons, Vanilla CSS (Glassmorphism).
- **Data**: Synthetic PUN (Italian Power) generator with real seasonality models.

---

## 🏃 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/enerlytics-nexus.git
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 📊 Strategic Impact
Enerlytics Nexus demonstrates a clear financial ROI, with simulated battery arbitrage strategies achieving up to **12-18% net savings** versus standard grid-only baselines in the Italian BTM market.

---
**Developed for the Solship Hackathon | 2026**
