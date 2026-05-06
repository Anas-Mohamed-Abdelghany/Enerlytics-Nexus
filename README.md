# 🌐 Enerlytics-Nexus
### *Global Financial & Commodity Intelligence Hub*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

**Enerlytics-Nexus** is a high-performance intelligence dashboard designed for global energy and commodity markets. It transforms raw data into actionable insights using multi-modal AI, real-time data normalization across 10+ APIs, and professional-grade financial visualizations.

---

## 🚀 Key Features

- **Multi-Asset Intelligence**: Integration with 10+ specialized data providers including US EIA, Ember, Alpha Vantage, and more.
- **Predictive Analytics Suite**: Dual-mode forecasting for price regression and directional classification using LSTM & Bi-LSTM models.
- **Strategy Optimization Engine**: Automated evaluation of trading models (Trend Trading, Mean Reversion) to identify market fit.
- **Professional UI/UX**: A modern, glassmorphism-inspired dashboard featuring high-precision Plotly multi-pane charts and Klinecharts.
- **Explainable AI (XAI)**: Understand the "why" behind every prediction with feature importance visualizations.
- **Risk Management**: Probabilistic forecasting using Stochastic Modeling (GARCH) and Monte Carlo simulations.

---

## 📸 Dashboard Preview
*(Images will be added here)*
> ![Main Dashboard Placeholder](https://via.placeholder.com/1200x600?text=Enerlytics+Nexus+Main+Dashboard)
> *Figure 1: Main Intelligence Hub displaying real-time commodity data and AI signals.*

---

## 🧠 AI Strategy & Forecasting Hub

### 1. Neural Architectures
- **LSTM / Bi-LSTM**: Advanced time-series analysis for capturing long-term dependencies in volatile energy markets.
- **Hybrid "Deep Stochastic" Model**: Combines Deep Learning (Central Path) with Stochastic Volatility (GARCH) to provide a full spectrum of possible outcomes via Monte Carlo simulations.

### 2. Market Intelligence Tools
- **Technical Indicators**: RSI, Bollinger Bands, Moving Averages, and more via `pandas-ta`.
- **Confidence Intervals**: Shaded Plotly overlays visualizing model certainty levels.
---

## 🛠️ Technology Stack

### **Frontend**
- **Framework**: React.js (Vite)
- **Charting**: Klinecharts, Recharts, ApexCharts, Plotly
- **Icons**: Lucide React
- **Styling**: Modern Vanilla CSS (Glassmorphism)

### **Backend**
- **API Framework**: FastAPI (Python)
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: TensorFlow, Scikit-learn
- **Technical Analysis**: Pandas-TA
- **Server**: Uvicorn

---

## 📂 Project Structure

```text
Enerlytics-Nexus/
├── backend/                # FastAPI Application
│   ├── api/                # Route Handlers
│   ├── core/               # Business Logic & Normalization
│   ├── models/             # AI/ML Models (LSTM, GARCH)
│   └── config/             # Configuration & API Keys
├── frontend/               # React + Vite Application
│   ├── src/                # Components & Hooks
│   ├── styles/             # Modern CSS Modules
│   └── public/             # Static Assets
└── Project.md              # Detailed Feature Roadmap
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

---

## 🌐 Data Intelligence Ecosystem
We integrate with the world's leading energy and financial data providers:
- **US EIA (v2)**: US Macro Energy Statistics.
- **Ember Energy**: Global electricity and climate data.
- **Alpha Vantage / FMP / Polygon**: Real-time stock, forex, and commodity feeds.
- **Energi Data Service**: Specialized Denmark/European energy metrics.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ for the Global Energy Future.*
