import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
from typing import List, Dict
from models.schemas import OHLCVPoint

def generate_plotly_chart(series: List[OHLCVPoint], ticker: str = "Market", theme: str = "dark", chart_type: str = "candlestick", indicators: List[str] = None) -> Dict[str, str]:
    """
    Generates a dictionary of Plotly HTML chart strings from OHLCV data.
    """
    if indicators is None:
        indicators = ["MA", "BOLL"]


    df = pd.DataFrame([p.model_dump() for p in series])
    
    # Ensure correct types for technical analysis
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate Indicators
    if "MACD" in indicators:
        df.ta.macd(close='close', append=True)
    if "RSI" in indicators:
        df.ta.rsi(close='close', append=True)
    if "BOLL" in indicators:
        df.ta.bbands(close='close', length=20, append=True)
    if "CCI" in indicators:
        df.ta.cci(close='close', append=True)
    if "ATR" in indicators:
        df.ta.atr(append=True)
    
    if "MA" in indicators or "SMA" in indicators:
        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA200'] = df['close'].rolling(window=200).mean()
    if "EMA" in indicators:
        df['EMA20'] = df.ta.ema(close='close', length=20)
    if "WMA" in indicators:
        df['WMA20'] = df.ta.wma(close='close', length=20)
    if "SAR" in indicators:
        df.ta.psar(append=True)

    
    # Fill NaNs
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    
    # Rename for Plotly (Plotly trace names often use these)
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], unit='ms')
    template = "plotly_dark" if theme == "dark" else "plotly_white"
    text_color = 'white' if theme == 'dark' else 'black'
    
    results = {}
    
    # Ensure is_forecast is present and correctly typed
    if 'is_forecast' not in df.columns:
        df['is_forecast'] = False
    else:
        df['is_forecast'] = df['is_forecast'].fillna(False).astype(bool)
    
    # Split historical vs forecast
    df_hist = df[df['is_forecast'] == False].copy()
    df_fore = df[df['is_forecast'] == True].copy()

    # 1. Main Price Chart
    fig_main = go.Figure()
    is_candlestick = chart_type in ["candlestick", "candle_solid", "candle_stroke"]
    
    if is_candlestick:
        fig_main.add_trace(go.Candlestick(
            x=df_hist['timestamp_dt'], 
            open=df_hist['Open'], high=df_hist['High'], low=df_hist['Low'], close=df_hist['Close'], 
            name='Historical'
        ))
    elif chart_type == "ohlc":
        fig_main.add_trace(go.Ohlc(
            x=df_hist['timestamp_dt'], 
            open=df_hist['Open'], high=df_hist['High'], low=df_hist['Low'], close=df_hist['Close'], 
            name='Historical'
        ))
    else:
        fill = 'tonexty' if chart_type == "area" else None
        fig_main.add_trace(go.Scatter(x=df_hist['timestamp_dt'], y=df_hist['Close'], mode='lines', name='Historical', fill=fill, line=dict(width=2)))

    # Forecast Trace
    if not df_fore.empty:
        # Join historical and forecast for a continuous line
        last_hist = df_hist.iloc[-1:]
        df_fore_conn = pd.concat([last_hist, df_fore])
        
        # Confidence Interval Shading
        if 'upper_ci' in df_fore_conn.columns and 'lower_ci' in df_fore_conn.columns:
            fig_main.add_trace(go.Scatter(
                x=pd.concat([df_fore_conn['timestamp_dt'], df_fore_conn['timestamp_dt'][::-1]]),
                y=pd.concat([df_fore_conn['upper_ci'], df_fore_conn['lower_ci'][::-1]]),
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name='Confidence Interval'
            ))

        fig_main.add_trace(go.Scatter(
            x=df_fore_conn['timestamp_dt'], 
            y=df_fore_conn['Close'], 
            mode='lines', 
            name='AI Forecast', 
            line=dict(color='var(--accent-primary)', width=3, dash='dash')
        ))

    # Overlays on Main
    if "MA" in indicators:
        if 'MA50' in df.columns:
            fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df['MA50'], mode='lines', name='MA50', line=dict(color='blue', width=1)))
        if 'MA200' in df.columns:
            fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df['MA200'], mode='lines', name='MA200', line=dict(color='purple', width=1)))
    
    if "EMA" in indicators and 'EMA20' in df.columns:
        fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df['EMA20'], mode='lines', name='EMA20', line=dict(color='orange', width=1)))
    
    if "WMA" in indicators and 'WMA20' in df.columns:
        fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df['WMA20'], mode='lines', name='WMA20', line=dict(color='pink', width=1)))

    if "SAR" in indicators:
        sar_cols = [c for c in df.columns if c.startswith('PSARL') or c.startswith('PSARS')]
        if sar_cols:
            fig_main.add_trace(go.Scatter(x=df_hist['timestamp_dt'], y=df_hist[sar_cols[0]], mode='markers', name='Parabolic SAR', marker=dict(size=4, color='white' if theme == 'dark' else 'black')))

    if "BOLL" in indicators:
        bbu_col = [c for c in df.columns if c.startswith('BBU')][0] if any(c.startswith('BBU') for c in df.columns) else None
        bbl_col = [c for c in df.columns if c.startswith('BBL')][0] if any(c.startswith('BBL') for c in df.columns) else None
        if bbu_col:
            fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[bbu_col], mode='lines', name='Upper Band', line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash')))
        if bbl_col:
            fig_main.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[bbl_col], mode='lines', name='Lower Band', line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash')))

    fig_main.update_layout(
        template=template,
        title=f"{ticker.upper()} Price Action",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
    )
    results['main'] = fig_main.to_html(
        full_html=False, 
        include_plotlyjs='cdn',
        config={
            'modeBarButtonsToAdd': [
                'drawline', 
                'drawopenpath', 
                'drawclosedpath', 
                'drawcircle', 
                'drawrect', 
                'eraseshape'
            ],
            'displaylogo': False,
            'responsive': True
        }
    )


    # 2. MACD Chart
    if "MACD" in indicators:
        fig_macd = go.Figure()
        macd_cols = [c for c in df.columns if c.startswith('MACD_') and not c.endswith('_s') and not c.endswith('_h')]
        signal_cols = [c for c in df.columns if c.startswith('MACDs_')]
        hist_cols = [c for c in df.columns if c.startswith('MACDh_')]
        
        if macd_cols:
            fig_macd.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[macd_cols[0]], name='MACD', line=dict(color='green')))
        if signal_cols:
            fig_macd.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[signal_cols[0]], name='Signal', line=dict(color='red', dash='dash')))
        if hist_cols:
            fig_macd.add_trace(go.Bar(x=df['timestamp_dt'], y=df[hist_cols[0]], name='Histogram', marker_color='grey'))
            
        fig_macd.update_layout(
            template=template, title="MACD", height=250, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
        )
        results['MACD'] = fig_macd.to_html(full_html=False, include_plotlyjs='cdn')

    # 3. RSI Chart
    if "RSI" in indicators:
        fig_rsi = go.Figure()
        rsi_cols = [c for c in df.columns if c.startswith('RSI_')]
        if rsi_cols:
            fig_rsi.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[rsi_cols[0]], name='RSI', line=dict(color='cyan')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            
        fig_rsi.update_layout(
            template=template, title="RSI", height=250, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
        )
        results['RSI'] = fig_rsi.to_html(full_html=False, include_plotlyjs='cdn')

    # 4. CCI Chart
    if "CCI" in indicators:
        fig_cci = go.Figure()
        cci_cols = [c for c in df.columns if c.startswith('CCI_')]
        if cci_cols:
            fig_cci.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[cci_cols[0]], name='CCI', line=dict(color='gold')))
            fig_cci.add_hline(y=100, line_dash="dash", line_color="red")
            fig_cci.add_hline(y=-100, line_dash="dash", line_color="green")
            
        fig_cci.update_layout(
            template=template, title="CCI", height=250, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
        )
        results['CCI'] = fig_cci.to_html(full_html=False, include_plotlyjs='cdn')

    # 5. ATR Chart
    if "ATR" in indicators:
        fig_atr = go.Figure()
        atr_cols = [c for c in df.columns if c.startswith('ATR_')]
        if atr_cols:
            fig_atr.add_trace(go.Scatter(x=df['timestamp_dt'], y=df[atr_cols[0]], name='ATR', line=dict(color='orange')))
            
        fig_atr.update_layout(
            template=template, title="ATR", height=250, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
        )
        results['ATR'] = fig_atr.to_html(full_html=False, include_plotlyjs='cdn')

    # 6. Specialized Forecast Chart
    if not df_fore.empty:
        try:
            fig_fore = go.Figure()
            # Add last few historical points for context
            df_context = df_hist.tail(15) if not df_hist.empty else df_hist
            df_fore_plot = pd.concat([df_context, df_fore])
            
            # Use markers only for the forecast part to distinguish
            fig_fore.add_trace(go.Scatter(
                x=df_fore_plot['timestamp_dt'], 
                y=df_fore_plot['Close'], 
                mode='lines+markers', 
                name='AI Forecast', 
                line=dict(color='#06b6d4', width=3),
                marker=dict(size=4, color='#06b6d4')
            ))
            
            # If CI exists, add it
            if 'upper_ci' in df_fore.columns and 'lower_ci' in df_fore.columns:
                # Need context for CI too if we want a smooth line
                fig_fore.add_trace(go.Scatter(
                    x=pd.concat([df_fore['timestamp_dt'], df_fore['timestamp_dt'][::-1]]),
                    y=pd.concat([df_fore['upper_ci'], df_fore['lower_ci'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(6, 182, 212, 0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    showlegend=False
                ))

            fig_fore.update_layout(
                template=template, title="Detailed AI Forecast", height=300, margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color))
            )
            results['forecast'] = fig_fore.to_html(full_html=False, include_plotlyjs='cdn')
        except Exception as e:
            print(f"Error generating specialized forecast chart: {e}")
            # Fallback: copy main if specialized fails
            if 'main' in results:
                results['forecast'] = results['main']


    return results



