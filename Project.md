uvicorn main:app --reload


# Enerlytics AI: Hackathon Feature List

This document outlines the high-performance features implemented in the **Enerlytics AI Dashboard**, transformed into a global financial and commodity intelligence hub.

---

## 🚀 Key Integrations & Data Intelligence

### 1. Multi-Asset Intelligence Ecosystem
*   **10+ Specialized Data Providers**: Full integration with Alpha Vantage, FMP, Polygon, Twelve Data, EOD, Ember Energy, Energi Data (Denmark), EnergypriceAPI, MetalpriceAPI, ForexRateAPI, and the **US EIA (v2)**.
*   **Global Market Reach**: Coverage across **Global Energy** (Brent, WTI), **Precious Metals** (Gold, Silver, Platinum), **Forex** (Major & Emerging Currencies like AED, INR), and **US Macro Energy Statistics**.
*   **Dynamic Ticker Mapping**: A server-driven mapping system that automatically updates UI dropdowns and ticker options based on the selected API provider's capabilities.

### 2. Advanced Backend Data Normalization
*   **Smart Frequency Engine**: Automatic resolution between **Annual** and **Monthly** data based on requested timeframes (optimized for EIA/Ember).
*   **Reciprocal Price Logic**: Intelligent backend calculation that converts raw currency/commodity rates (e.g., 1 USD = X) into standard market-friendly pricing (Price per unit in USD).
*   **RESTful Route Resolution**: Implementation of hierarchical path resolution for complex APIs like US EIA v2.

---

## 🧠 AI Strategy & Forecasting Hub

### 3. Predictive Analytics Suite
*   **Dual-Mode Forecasting**: Support for **Price Regression** (Target Price Prediction) and **Directional Classification** (Up/Down/Neutral trends).
*   **Neural Architectures**: Implementation of **LSTM** and **Bidirectional LSTM** models for time-series analysis.
*   **Interactive Confidence Intervals**: Visualizing model certainty with shaded Plotly overlays on historical data.

### 4. Strategy Optimization Engine
*   **Automated Strategy Selection**: A backend engine that evaluates multiple trading models (Trend Trading, Mean Reversion, etc.) and identifies the "Best Fit" for current market conditions.
*   **Real-Time Backtesting**: Simulating strategy performance over 1000+ data points to provide win rates and performance scores.

---

## 🎨 Professional UI/UX & Tools

### 5. High-Precision Visualizations
*   **Plotly Multi-Pane Charts**: Server-side rendered, interactive financial charts with support for OHLC, Candlestick, and multiple technical indicators (MA, Bollinger Bands, RSI).
*   **Glassmorphism Dashboard**: A modern, premium aesthetic using sleek transparency and vibrant accent colors.
*   **Adaptive UI Controls**: Context-aware selection menus that filter options (like Data Intervals) based on the specific data source's resolution.

### 6. Market Intelligence Tools
*   **Quick Convert Utility**: Built-in currency and commodity conversion tools integrated directly into the dashboard flow.
*   **KPI Tracking**: Real-time calculation of Volatility, Period Change, and Candle counts for any fetched dataset.
- **Model Selection (Bonus):** A dropdown to switch between different ML models you might have trained (e.g., ARIMA, LSTM, Prophet) and compare their forecasts.

### 3. Trading Strategy Simulator
- **Backtesting Section:** A dedicated page to run simulations on historical data.
- **Input Parameters:** Allow the user to set a start/end date and an initial virtual investment amount.
- **Results Display:**
    - **Profit & Loss (P&L):** Show the final profit or loss from the simulation.
    - **Return on Investment (ROI):** Display the P&L as a percentage.
    - **Trade Log:** A table showing every "BUY" and "SELL" action the AI took.
    - **Equity Curve:** A graph showing the portfolio's value over the simulation period.


## Tier 2: UI/UX Features (The Professional Polish)

*These features make your project look professional, polished, and easy for the judges to understand.*

### 4. Clean and Modern Design
- Use a dark theme with blue/white accents to match the hackathon branding.
- Ensure the website is fully responsive for both desktop and mobile viewing.

### 5. "How it Works" / About Page
- A clear, concise explanation of the project's goal and your solution.
- Briefly describe the models used, data sources, and the technical stack.
- Introduce your team members and their roles.

### 6. Simulated "Live Demo" Mode
- A "Live" button that simulates real-time data updates on the main chart.
- Include a "Recommended Action" box that shows the AI's current decision (BUY/SELL/HOLD) based on the simulated live data.


## Tier 3: Advanced Features (The "Wow Factor")

*Adding one or two of these can make a huge impression and set you apart from the competition.*

### 7. Multi-Factor Analysis
- **Weather Data Integration:** Show how external data like temperature or wind speed forecasts correlate with price predictions.
- **News Sentiment Analysis:** Use NLP to analyze energy-related news headlines and display a "market sentiment score."

### 8. Explainable AI (XAI) Dashboard
- A section that explains *why* the model made a certain prediction.
- Display a "Feature Importance" chart showing which factors (e.g., 'price 24h ago', 'weather forecast') were most influential.

### 9. Risk Management Profiles
- Allow the user to select a trading "personality" for the AI before running a simulation:
    - **Conservative:** Aims for small, safe gains.
    - **Aggressive:** Takes on more risk for potentially higher returns.
    - **Balanced:** A mix of the two.
- Show how P&L and trade frequency change based on the selected profile.


## Tier 4: Enterprise & Scalability Features (Think Like a Startup)

*These features demonstrate forward-thinking and an understanding of real-world applications.*

### 10. Portfolio Management Dashboard
- Allow users to create a virtual portfolio of multiple energy assets (e.g., German Power, US Natural Gas).
- Display overall portfolio value, P&L, risk exposure, and asset allocation.
- The AI can provide rebalancing suggestions.

### 11. API Endpoint Demonstration
- Create a simple, documented REST API for your model.
- Showcase example API calls and their JSON responses on a dedicated page.
  ```json
  // Example Request:
  GET /api/forecast?market=US-TEXAS&horizon=24h

  // Example Response:
  {
    "market": "US-TEXAS",
    "forecast": [
      {"timestamp": "...", "price": 45.50},
      {"timestamp": "...", "price": 46.20}
    ]
  }

### 12. Automated PDF Reporting
- A "Download Report" button that generates a professional PDF summary of a backtest simulation, including key metrics, charts, and top trades.

### 13. Custom Alerting System
- Allow users to set up custom email or on-screen notifications for:
    - **Price Alerts:** (e.g., "Price > $50/MWh").
    - **Volatility Alerts:** (e.g., "24h volatility > 15%").
    - **AI Signal Alerts:** (e.g., "AI issued a 'STRONG BUY' signal").


## Tier 5: Cutting-Edge AI & Research-Level Features (To Stun the Judges)

*Technically challenging features that show an exceptional level of expertise.*

### 14. Reinforcement Learning (RL) Trading Agent
- Train an RL agent (e.g., Deep Q-Network) that learns the optimal trading policy directly by "playing" the market game.
- Compare its performance to your primary forecast-based strategy.

### 15. Transformer-Based Forecasting Models
- Implement a state-of-the-art Transformer architecture (e.g., Time-Series Transformer, Informer) for time-series forecasting to capture long-range dependencies.

### 16. Generative AI for Market Simulation (GANs)
- Use a Generative Adversarial Network (GAN) to create thousands of realistic, synthetic future market scenarios.
- Stress-test your trading strategy against these scenarios to measure its robustness and calculate metrics like Value at Risk (VaR).

### 17. Multi-Modal Input Fusion
- Create a single model that ingests and processes multiple data types simultaneously:
    - **Numerical:** Prices, weather data.
    - **Text:** News headlines.
    - **Image:** Satellite imagery of infrastructure (highly ambitious).


## Tier 6: Gamification & User Engagement (To Make it Memorable)

*Features that make your demo interactive, educational, and fun.*

### 18. "Beat the AI" Trading Game
- A real-time game where a user can trade on a historical data segment and compare their final profit against the AI's profit over the same period.

### 19. Educational "Why?" Explanations
- An info icon next to AI recommendations that, when clicked, provides a plain-language explanation of the factors driving the decision.

### 20. Interactive Market Events Timeline
- Overlay clickable icons on the price chart for major historical events (e.g., geopolitical conflicts, plant outages) to show how the market reacted.

### 21. Backtesting Leaderboard
- A public leaderboard showing the most profitable simulations run on the platform, encouraging users to experiment with different parameters.


-----------------------------------------------------------------------------------------------------

# Mege API Application i Made:

### 1. The Pre-Built API Scraper: Your "Live Data Ingestion Engine"

This is your secret weapon. Instead of relying on a static dataset, you have a tool to get fresh data.

**What it is:** A dynamic data pipeline that can pull time-series data for any specified asset (which you call "currency") at a chosen interval.

**The Benefits:**

*   **Real-Time Relevance:** Your project isn't just a model trained on old data; it's a living system that can adapt to the latest market information. This is a massive plus.
*   **Flexibility & Scalability:** Your idea to have "currency" as a parameter is key. You can easily adapt your scraper to pull data for:
    *   German Day-Ahead Power Prices
    *   US Natural Gas Futures
    *   EU Carbon Credit Prices
    *   ...and your new idea, currency pairs like USD/CNY.
*   **Demonstrates End-to-End Capability:** You're not just doing the "glamorous" ML part; you're handling the entire data engineering pipeline, which is a critical real-world skill.

**How to Use It:**
1.  **Adapt for Energy:** Modify the scraper's endpoints to hit APIs for energy data (e.g., ENTSO-E for Europe, EIA for the US).
2.  **Automate It:** Set up a simple scheduler (like a cron job or a Python `schedule` script) to run your scraper every hour or every day. This will automatically download the latest data and append it to your CSVs.

---

### 2. The MLOps Pipeline: The "Self-Improving Brain"

This idea connects directly to your scraper and is arguably the most impressive feature you can build in a hackathon.

**What it is:** An automated workflow that uses the new data from your scraper to periodically re-train your machine learning model, ensuring it never becomes stale.

**The Benefits:**

*   **Dynamic Adaptation:** Your model learns from the most recent market behaviors, making its predictions far more accurate and relevant than a static model.
*   **Automation & Efficiency:** This shows you can build robust, hands-off systems. You're not manually re-training; the pipeline does it for you.
*   **Professional Standard:** MLOps is a hot-topic and a highly sought-after skill. Implementing even a simple version demonstrates you are far ahead of the curve.

**How to Implement a "Hackathon-Scale" MLOps Pipeline:**

You don't need complex tools like Kubeflow. You can script this easily. Here's the flow:

1.  **[Data Ingestion]**: Your scraper runs automatically on a schedule (e.g., every 6 hours) and appends new data to `energy_data.csv`.
2.  **[Trigger Training]**: After the scraper finishes, it triggers a `train_model.py` script.
3.  **[Model Training & Versioning]**: The script loads the updated CSV, re-trains the ML model, and saves the new model with a timestamp, e.g., `model_2026-05-09-1800.pkl`. It also saves the model's performance metrics (e.g., accuracy) to a log file.
4.  **[Model Deployment]**: Your web application is coded to automatically load and use the *latest* model file from the directory.

Your presentation can feature a diagram of this loop, showing how your AI is constantly learning and improving.

---

### 3. The Multi-Asset & Macroeconomic Data Merge: "The Smart Money"

This is your masterstroke. Merging energy data with currency data (like USD vs Yuan) is a sophisticated feature engineering technique used by real trading firms.

**What it is:** You're enriching your dataset with exogenous variables—external factors that influence the price of energy but aren't the price itself.

**Why USD/CNY is a brilliant choice:**
*   **Global Commodity Pricing:** Many energy contracts (especially oil and gas) are priced in USD. A stronger or weaker dollar directly impacts prices for buyers using other currencies.
*   **Global Manufacturing Hub:** China is the world's largest consumer of energy. The health of its currency (the Yuan/Renminbi) is a proxy for its economic activity. A strong Yuan might signal high industrial output and thus high energy demand.
*   **Geopolitical Indicator:** The USD/CNY exchange rate is sensitive to trade tensions and global economic policies, which also impact energy markets.

**The Benefits:**

*   **Increased Predictive Power:** Your model now has access to crucial context. It can learn complex relationships, such as "when the dollar strengthens and the yuan weakens, energy prices tend to dip." This will almost certainly improve its accuracy.
*   **Demonstrates Deep Thinking:** This shows you're not just throwing data at an algorithm. You have a hypothesis about how markets work and are testing it with data. The judges will be extremely impressed by this domain knowledge.
*   **Unlocks Explainable AI (XAI):** This is the perfect way to use your XAI dashboard (Feature #8). You can create a "Feature Importance" chart that visually proves that `USD_CNY_price` is one of the top 5 most important factors in predicting the energy price!

**How to Use It:**
1.  **Scrape Both:** Use your scraper to pull time-series data for both the energy source AND the USD/CNY exchange rate for the same time period.
2.  **Align & Merge:** This is a crucial data processing step. Make sure the timestamps from both datasets are aligned. You might need to forward-fill data if the currency markets were closed when the energy market was open. Merge them into a single CSV where each row has: `timestamp, energy_price, usd_cny_price`.
3.  **Train the Enriched Model:** Train your ML model on this new, richer dataset.
4.  **Showcase the Impact:** On your website, have a checkbox: "Include Macroeconomic Data." When checked, the model uses the enriched version, and you can show the forecast becomes more accurate. More importantly, you can display the feature importance chart to prove its value.


-----------------------------------------------------------------------------------------------------
# Stochastic Modeling and Deep Learning:

### Understanding the Roles

Think of your two approaches as two different specialists on a team:

**1. Your Role (Deep Learning): The Forecaster**
*   **What it does:** Deep Learning models (like LSTMs or Transformers) are masters of finding complex, non-linear patterns in data. They are excellent at learning from multiple features (price, volume, your USD/CNY data, weather, etc.) to produce a single, highly accurate "best guess" of where the price is headed.
*   **Its Output:** A **deterministic forecast**. It will tell you, "Based on everything I see, I predict the price will be $52.50 in 6 hours."
*   **Its Weakness:** It's often overconfident. It gives you one answer and struggles to naturally express the *uncertainty* or *risk* around that prediction.

**2. Your Friend's Role (Stochastic Modeling): The Risk Manager**
*   **What it does:** Stochastic models (like GARCH for volatility or Ornstein-Uhlenbeck for mean-reverting processes) are designed to model and quantify **randomness and uncertainty**. They don't just predict the price; they predict the *distribution* of possible prices.
*   **Its Output:** A **probabilistic forecast**. It will tell you, "The most likely price in 6 hours is around $52, but there's a 5% chance it could crash below $45 and a 5% chance it could spike above $60."
*   **Its Weakness:** It often relies on simplifying assumptions and can't easily incorporate the dozens of external features that a Deep Learning model can.

You see the synergy? One is great at prediction, the other is great at risk. Together, they are unstoppable.

---

### The Winning Strategy: A Hybrid "Deep Stochastic" Model

Here is a step-by-step plan to combine your skills. This is your project's new core architecture.

#### Step 1: Deep Learning Predicts the "Drift" (The Central Path)
You build your Deep Learning model (LSTM is a great choice) using all the rich features you've collected: historical energy prices, USD/CNY rates, and any other data.
*   **Input:** Time-series data with multiple features.
*   **Output:** The most probable price forecast for the next `N` hours. This is your **central prediction path**.

#### Step 2: Stochastic Modeling Predicts the "Volatility" (The Uncertainty)
While you're building the DL model, your friend builds a volatility model. The most common and effective choice here is a **GARCH (Generalized Autoregressive Conditional Heteroskedasticity)** model.
*   **Input:** The historical price returns (percent changes).
*   **Output:** A forecast of the future volatility (the standard deviation of returns). This tells you how "wild" or "calm" the market is likely to be.

#### Step 3: Combine them with a Monte Carlo Simulation
This is where the magic happens. You use the outputs from both models to simulate thousands of possible future scenarios.
1.  **Start with the DL Forecast:** Take your Deep Learning model's price path as the "center" or "mean" of your simulation.
2.  **Inject Stochastic Volatility:** For each future time step, add a random "shock" to the DL prediction. The size of this random shock is determined by the volatility predicted by your friend's GARCH model.
3.  **Run Thousands of Times:** Repeat this process 1,000s of times to generate a huge number of possible future price paths.

#### The Final Output: A Rich, Probabilistic Forecast

Instead of a single line on a chart, your website will now display a beautiful **"fan chart"**.
*   The **solid line in the middle** is your Deep Learning model's prediction.
*   The **shaded cones or bands** around it represent the 75%, 90%, and 95% confidence intervals generated by the Monte Carlo simulation.



### How This Elevates Your Project:

1.  **Advanced Risk Management:** You can now calculate critical risk metrics like **Value at Risk (VaR)**. You can state on your website: "Our AI's trading strategy aims for a 7% return while maintaining a 95% VaR of no more than 2%." This is professional-grade language.
2.  **Smarter Trading Strategy:** Your trading algorithm can now be much more sophisticated:
    *   **Simple Strategy:** BUY when the DL model predicts a price increase.
    *   **Hybrid Strategy:** BUY when the DL model predicts a price increase, **but only if the GARCH model predicts low volatility**. If volatility is high, the risk is too great, so you stay out of the market, preserving capital.
3.  **Unbeatable Presentation:** When you present to the judges, you can say:
    *"We developed a hybrid model that combines the predictive power of Deep Learning with the risk-management capabilities of stochastic modeling. Our LSTM model ingests macroeconomic data to forecast the likely price path, while our GARCH model quantifies market uncertainty. By integrating them via a Monte Carlo simulation, our platform doesn't just predict the future; it models the full spectrum of possible outcomes, enabling a truly robust and risk-aware trading strategy."*

### Division of Labor:
*   **You:** Focus on the data pipeline (scraper, feature engineering with USD/CNY), building and training the LSTM/Transformer model, and developing the frontend/website.
*   **Your Friend:** Focus on researching and implementing the GARCH model, building the Monte Carlo simulation engine that combines both outputs, and calculating the final risk metrics (VaR, confidence intervals).