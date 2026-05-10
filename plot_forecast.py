import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def plot_forecast(csv_path='forecast.csv'):
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return

    print(f"📊 Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure Timestamp is datetime
    ts_col = 'Timestamp' if 'Timestamp' in df.columns else ('timestamp' if 'timestamp' in df.columns else None)
    if ts_col:
        df[ts_col] = pd.to_datetime(df[ts_col])
        df.set_index(ts_col, inplace=True)
    else:
        print("❌ Error: No Timestamp column found.")
        return

    df = df.sort_index()

    # Check for required columns
    load_col = 'load' if 'load' in df.columns else ('load_p' if 'load_p' in df.columns else None)
    pred_col = 'predicted' if 'predicted' in df.columns else ('load_new' if 'load_new' in df.columns else None)

    if not load_col or not pred_col:
        available = list(df.columns)
        print(f"❌ Error: Could not find both 'load' and 'predicted' columns. Available: {available}")
        return

    # Filter for target months (4 and 9)
    target_months = [4, 9]
    month_names = {4: "April", 9: "September"}
    
    for month in target_months:
        month_df = df[df.index.month == month].copy()
        
        if month_df.empty:
            print(f"⚠️ Warning: No data found for month {month} ({month_names[month]})")
            continue

        month_name = month_names[month]
        print(f"📈 Plotting {month_name} ({len(month_df)} data points)...")
        
        plt.figure(figsize=(14, 7), facecolor='#0d1018')
        ax = plt.gca()
        ax.set_facecolor('#1a1a1a')

        plt.plot(month_df.index, month_df[load_col], label='Actual Load (Baseline)', color='#ff8c42', linewidth=1.5, alpha=0.8)
        plt.plot(month_df.index, month_df[pred_col], label='Predicted Load (AI)', color='#3b82f6', linewidth=1.5, alpha=0.9)

        # Calculate metrics
        mae = (month_df[load_col] - month_df[pred_col]).abs().mean()
        rmse = ((month_df[load_col] - month_df[pred_col])**2).mean()**0.5
        print(f"✅ {month_name} - MAE: {mae:.4f} | RMSE: {rmse:.4f}")

        # Styling
        plt.title(f'Energy Load Forecasting: {month_name} 2025 Audit', color='white', fontsize=16, pad=20)
        plt.xlabel('Time', color='white')
        plt.ylabel('Power (kW)', color='white')
        
        plt.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
        plt.grid(True, which='both', color='white', alpha=0.1)
        
        ax.tick_params(axis='x', colors='white', labelsize=9)
        ax.tick_params(axis='y', colors='white', labelsize=9)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        output_png = f'audit_plot_{month_name.lower()}.png'
        plt.savefig(output_png, dpi=300, facecolor='#0d1018')
        print(f"🚀 {month_name} Plot saved to {output_png}")
        plt.close() # Close figure to free memory

if __name__ == "__main__":
    # Robust file selection
    possible_files = ['forcast.csv', 'forecast.csv', '2nd_Forcast.csv']
    file_to_plot = None
    
    for f in possible_files:
        if os.path.exists(f):
            file_to_plot = f
            break
    
    if file_to_plot:
        plot_forecast(file_to_plot)
    else:
        print("❌ Error: No forecast CSV file found (tried forcast.csv, forecast.csv, 2nd_Forcast.csv)")
