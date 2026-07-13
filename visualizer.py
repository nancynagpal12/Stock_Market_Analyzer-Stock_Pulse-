import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from config import (CHARTS_DIR, CHART_THEME, CHART_WIDTH, CHART_HEIGHT,
                    COLOR_BULLISH, COLOR_BEARISH, COLOR_SMA_SHORT,
                    COLOR_SMA_LONG, COLOR_BOLLINGER)


def _save_chart(fig, filename):
    """Save chart as interactive HTML and static PNG."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    html_path = os.path.join(CHARTS_DIR, f"{filename}.html")
    fig.write_html(html_path)
    print(f"  Saved: {html_path}")
    try:
        png_path = os.path.join(CHARTS_DIR, f"{filename}.png")
        fig.write_image(png_path, width=CHART_WIDTH, height=CHART_HEIGHT)
        print(f"  Saved: {png_path}")
    except Exception:
        print(f"  PNG export skipped (install kaleido: pip install kaleido)")


def plot_candlestick(df, symbol="Stock"):
    """
    Candlestick chart with volume bars — the standard stock chart.
    Green candle = price went UP, Red candle = price went DOWN.
    """
    close_col = "Close" if "Close" in df.columns else "close"
    open_col = "Open" if "Open" in df.columns else "open"
    high_col = "High" if "High" in df.columns else "high"
    low_col = "Low" if "Low" in df.columns else "low"
    vol_col = "Volume" if "Volume" in df.columns else "volume"

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=[0.7, 0.3],
                        subplot_titles=[f"{symbol} — Price", "Volume"])

    fig.add_trace(go.Candlestick(
        x=df.index, open=df[open_col], high=df[high_col],
        low=df[low_col], close=df[close_col], name="Price",
        increasing_line_color=COLOR_BULLISH,
        decreasing_line_color=COLOR_BEARISH), row=1, col=1)

    if vol_col in df.columns:
        colors = [COLOR_BULLISH if df[close_col].iloc[i] >= df[open_col].iloc[i]
                  else COLOR_BEARISH for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df[vol_col], name="Volume",
                             marker_color=colors, opacity=0.5), row=2, col=1)

    fig.update_layout(template=CHART_THEME, title=f"{symbol} — Candlestick Chart",
                      xaxis_rangeslider_visible=False, showlegend=True,
                      width=CHART_WIDTH, height=CHART_HEIGHT)
    _save_chart(fig, f"{symbol}_candlestick")
    return fig


def plot_moving_averages(df, symbol="Stock"):
    """Price chart with SMA and EMA overlay lines."""
    close_col = "Close" if "Close" in df.columns else "close"
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df[close_col], name="Close Price",
                             line=dict(color="white", width=1.5)))

    if "SMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20",
                                 line=dict(color=COLOR_SMA_SHORT, width=1.5, dash="dot")))
    if "SMA_50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50",
                                 line=dict(color=COLOR_SMA_LONG, width=1.5, dash="dot")))
    if "EMA_12" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA_12"], name="EMA 12",
                                 line=dict(color="#FF6D00", width=1, dash="dash")))
    if "EMA_26" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA_26"], name="EMA 26",
                                 line=dict(color="#00BFA5", width=1, dash="dash")))

    fig.update_layout(template=CHART_THEME, title=f"{symbol} — Moving Averages",
                      yaxis_title="Price", width=CHART_WIDTH, height=CHART_HEIGHT)
    _save_chart(fig, f"{symbol}_moving_averages")
    return fig


def plot_rsi(df, symbol="Stock"):
    """RSI chart with overbought (70) and oversold (30) zones."""
    if "RSI" not in df.columns:
        print("  RSI data not found")
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#7C4DFF", width=2)))

    # Overbought/Oversold zones
    fig.add_hline(y=70, line_dash="dash", line_color=COLOR_BEARISH,
                  annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color=COLOR_BULLISH,
                  annotation_text="Oversold (30)")
    fig.add_hrect(y0=70, y1=100, fillcolor=COLOR_BEARISH, opacity=0.1)
    fig.add_hrect(y0=0, y1=30, fillcolor=COLOR_BULLISH, opacity=0.1)

    fig.update_layout(template=CHART_THEME, title=f"💪 {symbol} — RSI (Relative Strength Index)",
                      yaxis=dict(title="RSI", range=[0, 100]),
                      width=CHART_WIDTH, height=500)
    _save_chart(fig, f"{symbol}_rsi")
    return fig


def plot_macd(df, symbol="Stock"):
    """MACD chart with signal line and histogram."""
    if "MACD" not in df.columns:
        print("  MACD data not found")
        return None

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.5, 0.5])

    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                             line=dict(color="#2979FF", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"], name="Signal",
                             line=dict(color="#FF6D00", width=2)), row=1, col=1)

    if "MACD_Histogram" in df.columns:
        colors = [COLOR_BULLISH if v >= 0 else COLOR_BEARISH
                  for v in df["MACD_Histogram"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Histogram"],
                             name="Histogram", marker_color=colors, opacity=0.6),
                      row=2, col=1)

    fig.update_layout(template=CHART_THEME, title=f"{symbol} — MACD",
                      width=CHART_WIDTH, height=CHART_HEIGHT)
    _save_chart(fig, f"{symbol}_macd")
    return fig


def plot_bollinger_bands(df, symbol="Stock"):
    """Bollinger Bands chart with shaded volatility region."""
    close_col = "Close" if "Close" in df.columns else "close"
    if "Bollinger_Upper" not in df.columns:
        print("  Bollinger Bands data not found")
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["Bollinger_Upper"], name="Upper Band",
                             line=dict(color=COLOR_BOLLINGER, width=1, dash="dash")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Bollinger_Lower"], name="Lower Band",
                             line=dict(color=COLOR_BOLLINGER, width=1, dash="dash"),
                             fill="tonexty", fillcolor="rgba(171,71,188,0.1)"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Bollinger_Middle"], name="Middle (SMA)",
                             line=dict(color=COLOR_BOLLINGER, width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df[close_col], name="Close Price",
                             line=dict(color="white", width=1.5)))

    fig.update_layout(template=CHART_THEME, title=f"{symbol} — Bollinger Bands",
                      yaxis_title="Price", width=CHART_WIDTH, height=CHART_HEIGHT)
    _save_chart(fig, f"{symbol}_bollinger")
    return fig


def plot_comparison(stock_data_dict):
    """Compare multiple stocks on one normalized chart (base = 100)."""
    fig = go.Figure()

    for symbol, df in stock_data_dict.items():
        close_col = "Close" if "Close" in df.columns else "close"
        if close_col in df.columns and len(df) > 0:
            first_price = df[close_col].iloc[0]
            if first_price > 0:
                normalized = (df[close_col] / first_price) * 100
                fig.add_trace(go.Scatter(x=df.index, y=normalized,
                                         name=symbol, mode="lines"))

    fig.update_layout(template=CHART_THEME,
                      title="Multi-Stock Comparison (Normalized to 100)",
                      yaxis_title="Normalized Price (Base = 100)",
                      width=CHART_WIDTH, height=CHART_HEIGHT)
    _save_chart(fig, "stock_comparison")
    return fig


def plot_full_dashboard(df, symbol="Stock"):
    """
    Complete analysis dashboard — 4 panels in one view:
    1. Candlestick + Moving Averages
    2. Volume
    3. RSI
    4. MACD
    """
    close_col = "Close" if "Close" in df.columns else "close"
    open_col = "Open" if "Open" in df.columns else "open"
    high_col = "High" if "High" in df.columns else "high"
    low_col = "Low" if "Low" in df.columns else "low"
    vol_col = "Volume" if "Volume" in df.columns else "volume"

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.4, 0.15, 0.2, 0.25],
                        subplot_titles=["Price & Moving Averages", "Volume",
                                        "RSI", "MACD"])

    # Row 1: Candlestick + SMAs
    fig.add_trace(go.Candlestick(
        x=df.index, open=df[open_col], high=df[high_col],
        low=df[low_col], close=df[close_col], name="Price",
        increasing_line_color=COLOR_BULLISH,
        decreasing_line_color=COLOR_BEARISH), row=1, col=1)

    if "SMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20",
                                 line=dict(color=COLOR_SMA_SHORT, width=1)), row=1, col=1)
    if "SMA_50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50",
                                 line=dict(color=COLOR_SMA_LONG, width=1)), row=1, col=1)

    # Row 2: Volume
    if vol_col in df.columns:
        colors = [COLOR_BULLISH if df[close_col].iloc[i] >= df[open_col].iloc[i]
                  else COLOR_BEARISH for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df[vol_col], name="Volume",
                             marker_color=colors, opacity=0.5), row=2, col=1)

    # Row 3: RSI
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                                 line=dict(color="#7C4DFF", width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color=COLOR_BEARISH, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color=COLOR_BULLISH, row=3, col=1)

    # Row 4: MACD
    if "MACD" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                                 line=dict(color="#2979FF", width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"], name="Signal",
                                 line=dict(color="#FF6D00", width=1.5)), row=4, col=1)

    fig.update_layout(template=CHART_THEME,
                      title=f"{symbol} — Complete Analysis Dashboard",
                      xaxis_rangeslider_visible=False, showlegend=True,
                      width=CHART_WIDTH, height=1000)
    _save_chart(fig, f"{symbol}_dashboard")
    return fig


def generate_all_charts(df, symbol="Stock"):
    """Generate all chart types for a stock."""
    print(f"\nGenerating charts for {symbol}...")
    charts = {}
    charts["candlestick"] = plot_candlestick(df, symbol)
    charts["moving_averages"] = plot_moving_averages(df, symbol)
    charts["rsi"] = plot_rsi(df, symbol)
    charts["macd"] = plot_macd(df, symbol)
    charts["bollinger"] = plot_bollinger_bands(df, symbol)
    charts["dashboard"] = plot_full_dashboard(df, symbol)
    print(f"  All charts generated for {symbol}!\n")
    return charts
