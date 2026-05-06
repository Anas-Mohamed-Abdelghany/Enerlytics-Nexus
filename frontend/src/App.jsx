import React, { useState, useEffect } from "react";
import { Activity, Sun, Moon } from "lucide-react";
import Dashboard from "./modules/Dashboard";
import Forecaster from "./modules/Forecaster";

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Apply theme to document body
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.remove('light-mode');
    } else {
      document.body.classList.add('light-mode');
    }
  }, [isDarkMode]);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  return (
    <div className="app-layout">
      {/* Top Navigation */}
      <header className="top-navbar">
        <div className="logo-text">
          <Activity size={28} color="var(--accent-secondary)" />
          Enerlytics AI
        </div>
        <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle Theme">
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </header>

      {/* Main Content Grid */}
      <main className="main-content">
        <div className="dashboard-grid">
          {/* Historical Data takes full width on top */}
          <div className="full-width">
            <Dashboard isDarkMode={isDarkMode} />
          </div>


        </div>
      </main>
    </div>
  );
}
