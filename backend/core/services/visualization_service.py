import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os
from .energy_tariff_service import get_tou_band

def plot_march_week3_dispatch(df_results: pd.DataFrame, save_path: str = 'results/march_week3_dispatch.png'):
    """
    Generates a 5-panel publication-quality dispatch plot for the March 2025 Golden Window.
    """
    # 1. Setup & Filtering
    df = df_results.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter to Week 3 (March 17-23, 2025)
    start_date = '2025-03-17'
    end_date = '2025-03-24' # Exclusive
    week3 = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)].sort_values('timestamp')
    
    if week3.empty:
        print("Warning: No data found for March Week 3 2025.")
        return

    # Solship Colors
    NAVY = "#1B2A4A"
    GOLD = "#F5A623"
    GREEN = "#27AE60"
    RED = "#E74C3C"
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 10
    
    fig, axes = plt.subplots(5, 1, figsize=(16, 12), sharex=True, dpi=150)
    plt.subplots_adjust(hspace=0.2)
    
    # --- Helper: Shading Tariff Bands ---
    def shade_tariffs(ax):
        # We look at each hour in the week
        t_range = week3['timestamp']
        for i in range(len(week3) - 1):
            ts = t_range.iloc[i]
            next_ts = t_range.iloc[i+1]
            band = get_tou_band(ts)
            
            # F1: Light Red, F2: Light Yellow, F3: Light Blue
            color = "#FADBD8" if band == "F1" else "#FCF3CF" if band == "F2" else "#D6EAF8"
            ax.axvspan(ts, next_ts, color=color, alpha=0.3, lw=0)

    # 2. Subplots
    
    # Subplot 1: Load
    shade_tariffs(axes[0])
    axes[0].plot(week3['timestamp'], week3['load_kw'], color='#2980B9', lw=1.5, label='Load')
    axes[0].set_ylabel('Load (kW)')
    axes[0].set_ylim(0, max(week3['load_kw']) * 1.2)
    
    # Subplot 2: PV
    shade_tariffs(axes[1])
    axes[1].fill_between(week3['timestamp'], week3['pv_kw'], color=GOLD, alpha=0.7, label='PV Solar')
    axes[1].set_ylabel('PV (kW)')
    
    # Subplot 3: Battery Power
    shade_tariffs(axes[2])
    p_bat = week3['p_battery_kw'].values
    axes[2].fill_between(week3['timestamp'], p_bat, 0, where=(p_bat >= 0), color=GREEN, alpha=0.8, label='Discharge')
    axes[2].fill_between(week3['timestamp'], p_bat, 0, where=(p_bat < 0), color=RED, alpha=0.8, label='Charge')
    axes[2].axhline(0, color='black', lw=0.8, alpha=0.5)
    axes[2].set_ylabel('Battery (kW)')
    axes[2].set_ylim(-9, 9)
    
    # Subplot 4: Grid Power
    shade_tariffs(axes[3])
    p_grid = week3['p_grid_actual'].values # Note: using column name from run_full_year results
    axes[3].fill_between(week3['timestamp'], p_grid, 0, where=(p_grid >= 0), color=GREEN, alpha=0.8, label='Import')
    axes[3].fill_between(week3['timestamp'], p_grid, 0, where=(p_grid < 0), color=RED, alpha=0.8, label='Export')
    axes[3].axhline(0, color='black', lw=0.8, alpha=0.5)
    axes[3].set_ylabel('Grid (kW)')
    axes[3].set_ylim(-7, 7)
    
    # Subplot 5: State of Charge
    shade_tariffs(axes[4])
    # Ensure soc is in %
    soc_data = week3['soc'].values
    if np.max(soc_data) <= 1.05: soc_data *= 100
    
    axes[4].fill_between(week3['timestamp'], soc_data, color=NAVY, alpha=0.8, label='SoC')
    axes[4].axhline(0, color='black', lw=1, ls='--')
    axes[4].axhline(50, color='black', lw=1, ls='--', alpha=0.3)
    axes[4].axhline(100, color='black', lw=1, ls='--')
    axes[4].set_ylabel('SoC (%)')
    axes[4].set_ylim(-5, 105)

    # 3. Final Formatting
    axes[4].xaxis.set_major_locator(mdates.DayLocator())
    axes[4].xaxis.set_major_formatter(mdates.DateFormatter('%a\n%b %d'))
    plt.xticks(rotation=0)
    
    # Title & Branding
    savings_text = ""
    if 'bill_per_step' in week3.columns:
        total_week_bill = week3['bill_per_step'].sum()
        # Baseline B (Passive) proxy for subtitle
        net_load = week3['load_kw'].values - week3['pv_kw'].values
        # Simple buy/sell proxy
        bill_b = np.sum(np.maximum(0, net_load) * 0.25 * 0.25) 
        savings = bill_b - total_week_bill
        savings_text = f" | Est. Savings vs Passive: €{savings:.2f}"

    fig.suptitle("Week 3 March 2025 — Battery Dispatch Strategy", fontsize=18, fontweight='bold', color=NAVY, y=0.95)
    axes[0].set_title(f"Competitive Optimization Results{savings_text}", fontsize=12, color=NAVY, alpha=0.7)

    # Custom Legend for Tariffs
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#FADBD8', alpha=0.5, label='F1 (Peak)'),
        Patch(facecolor='#FCF3CF', alpha=0.5, label='F2 (Mid)'),
        Patch(facecolor='#D6EAF8', alpha=0.5, label='F3 (Off)'),
        Patch(facecolor=GREEN, alpha=0.8, label='Import/Discharge'),
        Patch(facecolor=RED, alpha=0.8, label='Export/Charge')
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.94), ncol=5, frameon=False)

    # Save
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Success: Dispatch plot saved to {save_path}")

def plot_forecast_vs_actual(y_true: np.ndarray, y_pred: np.ndarray, timestamps: pd.Series, title: str, save_path: str = 'results/forecast_vs_actual.png'):
    """
    Plots forecast vs actual with error bands and an inset error distribution.
    """
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    
    # Take last week for clarity
    N = min(len(y_true), 672) # 7 days at 15m
    t = timestamps.iloc[-N:]
    y_t = y_true[-N:]
    y_p = y_pred[-N:]

    fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
    
    # 1. Shading F1 Tariff (Peak)
    for i in range(len(t) - 1):
        band = get_tou_band(t.iloc[i])
        if band == "F1":
            ax.axvspan(t.iloc[i], t.iloc[i+1], color='#FADBD8', alpha=0.3, lw=0)

    # 2. Main Plot
    ax.plot(t, y_t, color='#1B2A4A', label='Actual Load', lw=1.5)
    ax.plot(t, y_p, color='#F5A623', ls='--', label='Forecast', lw=1.5)
    ax.fill_between(t, y_p - rmse, y_p + rmse, color='#F5A623', alpha=0.15, label='±1 RMSE Band')
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Load (kW)')
    ax.legend(loc='upper left', frameon=False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d\n%b'))
    
    # 3. Inset Histogram
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    ax_ins = inset_axes(ax, width="25%", height="25%", loc='upper right', borderpad=3)
    errors = y_true - y_pred
    ax_ins.hist(errors, bins=30, color='#1B2A4A', alpha=0.7)
    ax_ins.axvline(0, color='red', lw=1, alpha=0.5)
    ax_ins.set_title('Error Dist.', fontsize=9)
    ax_ins.tick_params(labelsize=8)

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
        
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Success: Forecast comparison plot saved to {save_path}")
