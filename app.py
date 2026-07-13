import streamlit as st
import pandas as pd
import time
from config import DEFAULT_STOCKS, RSI_OVERBOUGHT, RSI_OVERSOLD
from database import (initialize_database, get_all_stocks, get_stock_data, 
                      insert_stock, insert_price_data, insert_indicators)
from data_fetcher import fetch_stock_data, fetch_company_info
from technical_analysis import run_full_analysis
from visualizer import plot_full_dashboard
from report_generator import generate_stock_report

st.set_page_config(
    page_title="Stock Market Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB on startup
@st.cache_resource
def setup_db():
    initialize_database()

setup_db()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Metric Cards with Glassmorphism & Hover Effects */
    .metric-card {
        background: linear-gradient(145deg, #1e1e2f, #252538);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 25px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        text-align: center;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-label {
        color: #8A91B6;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: #1e1e2f;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 25px;
        font-weight: 600;
        color: #8A91B6;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #252538;
        color: #FFFFFF;
    }
    .stTabs [aria-selected="true"] {
        background-color: #292d3e;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 3px solid #ff79c6;
    }

    /* ── Sidebar Core ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #161621 50%, #1a1a2e 100%) !important;
        border-right: 1px solid rgba(255, 121, 198, 0.12) !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    /* Crush excessive top/bottom spacing on all sidebar block wrappers */
    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] .element-container,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stSidebar"] .stElementContainer {
        margin-bottom: 6px !important;
    }
    /* ── Sidebar Labels ── */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] .stWidgetLabel p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #C8CFEA !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        -webkit-text-fill-color: #C8CFEA !important;
        margin-bottom: 3px !important;
    }
    /* ── Text Input ── */
    [data-testid="stSidebar"] .stTextInput input {
        color: #111111 !important;
        background-color: #f5f5f8 !important;
        border: 1px solid rgba(255, 121, 198, 0.35) !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
        height: 38px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #888 !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #FF79C6 !important;
        box-shadow: 0 0 0 2px rgba(255, 121, 198, 0.25), 0 0 16px rgba(255, 121, 198, 0.12) !important;
        background-color: #ffffff !important;
        outline: none !important;
        color: #111111 !important;
    }
    /* ── Selectbox ── */
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #f5f5f8 !important;
        border: 1px solid rgba(255, 121, 198, 0.35) !important;
        border-radius: 8px !important;
        height: 38px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"]:focus-within {
        border-color: #FF79C6 !important;
        box-shadow: 0 0 0 2px rgba(255, 121, 198, 0.25), 0 0 16px rgba(255, 121, 198, 0.12) !important;
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #111111 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    /* ── Sidebar Button ── */
    [data-testid="stSidebar"] .stButton > button {
        margin-top: 4px !important;
        padding: 9px 0 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] [data-testid="stExpanderToggleDetails"] {
        color: #E2E8F0 !important;
        -webkit-text-fill-color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    [data-testid="stExpander"] {
        background: linear-gradient(145deg, #1e1e2f, #252538) !important;
        border: 1px solid rgba(255, 121, 198, 0.18) !important;
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(189, 147, 249, 0.35) !important;
        box-shadow: 0 6px 28px rgba(0, 0, 0, 0.35);
    }
    [data-testid="stExpander"] summary {
        padding: 14px 18px !important;
        cursor: pointer;
    }
    /* Arrow / toggle icon */
    [data-testid="stExpander"] summary svg {
        fill: #BD93F9 !important;
        stroke: #BD93F9 !important;
        transition: transform 0.25s ease;
    }
    /* Inner content area */
    [data-testid="stExpander"] [data-testid="stExpanderDetails"],
    [data-testid="stExpander"] .streamlit-expanderContent {
        color: #C8CFEA !important;
        -webkit-text-fill-color: #C8CFEA !important;
        background: rgba(15, 15, 26, 0.4) !important;
        padding: 12px 18px 16px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    /* Expander inside sidebar */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: linear-gradient(145deg, #161621, #1a1a2e) !important;
        border: 1px solid rgba(255, 121, 198, 0.15) !important;
    }

    /* Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #FF79C6, #BD93F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #BD93F9, #FF79C6);
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(189, 147, 249, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(189, 147, 249, 0.6);
        color: white;
    }
    
    /* Responsive grid fix for cards */
    @media (max-width: 768px) {
        .metric-value { font-size: 24px; }
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(255,121,198,0.12), rgba(189,147,249,0.12));
    border: 1px solid rgba(255,121,198,0.2);
    border-radius: 12px;
    padding: 16px 18px 14px;
    margin-bottom: 18px;
">
    <div style="
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 1.2px;
        background: linear-gradient(90deg, #FF79C6, #BD93F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 0.9;
    ">StockPulse</div>
    <div style="color: #6B7280; font-size: 11px; letter-spacing: 0.5px;">Market Data & Insights</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #FF79C6;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
">
    <span style="display:inline-block;width:16px;height:2px;background:linear-gradient(90deg,#FF79C6,#BD93F9);border-radius:2px;vertical-align:middle;"></span>
    Fetch New Data
    <span style="flex:1;height:1px;background:rgba(255,121,198,0.15); border-radius:2px;"></span>
</div>
""", unsafe_allow_html=True)

fetch_symbol = st.sidebar.text_input("Ticker Symbol", placeholder="e.g. AAPL, RELIANCE.NS", value="", label_visibility="visible").upper()
fetch_period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, label_visibility="visible")

if st.sidebar.button("Fetch & Analyze", use_container_width=True):
    if fetch_symbol:
        with st.sidebar.status(f"Fetching {fetch_symbol}...") as status:
            st.write("Getting company info...")
            info = fetch_company_info(fetch_symbol)
            stock_id = insert_stock(fetch_symbol, info["name"], info["sector"], info["market_cap"])
            st.write("Downloading price data...")
            df = fetch_stock_data(fetch_symbol, period=fetch_period)
            if not df.empty:
                st.write("Running technical analysis...")
                insert_price_data(stock_id, df)
                analysis_df = run_full_analysis(df)
                insert_indicators(stock_id, analysis_df)
                status.update(label="Done!", state="complete", expanded=False)
                st.session_state['selected_ticker'] = fetch_symbol
                time.sleep(0.8)
                st.rerun()
            else:
                status.update(label="Failed. Check ticker symbol.", state="error")
    else:
        st.sidebar.error("Please enter a ticker symbol.")

st.sidebar.markdown("""
<div style="
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #BD93F9;
    margin-top: 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
">
    <span style="display:inline-block;width:16px;height:2px;background:linear-gradient(90deg,#BD93F9,#FF79C6);border-radius:2px;vertical-align:middle;"></span>
    Analyze Stock
    <span style="flex:1;height:1px;background:rgba(189,147,249,0.15);border-radius:2px;"></span>
</div>
""", unsafe_allow_html=True)

stocks_df = get_all_stocks()

if stocks_df.empty:
    st.warning("No stocks in database. Please fetch data first.")
    st.stop()

stock_options = stocks_df['symbol'].tolist()

default_idx = 0
if 'selected_ticker' in st.session_state and st.session_state['selected_ticker'] in stock_options:
    default_idx = stock_options.index(st.session_state['selected_ticker'])

selected_stock = st.sidebar.selectbox("Select Stock", stock_options, index=default_idx, label_visibility="visible")
st.session_state['selected_ticker'] = selected_stock

# Get selected stock details
stock_info = stocks_df[stocks_df['symbol'] == selected_stock].iloc[0]


# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"{stock_info['company_name']} ({selected_stock})")
    st.caption(f"Sector: {stock_info['sector']} | Market Cap: {stock_info['market_cap']}")

# Load Data
with st.spinner("Loading analysis..."):
    price_df = get_stock_data(selected_stock)
    if price_df.empty:
        st.error(f"No price data found for {selected_stock}. Please fetch data again.")
        st.stop()
    
    # We dynamically calculate analysis to ensure it's fresh
    analysis_df = run_full_analysis(price_df)
    # Merge for chart
    merged_df = price_df.join(analysis_df.drop(columns=[c for c in analysis_df.columns if c in price_df.columns], errors="ignore"))
    latest = merged_df.iloc[-1]
    first = merged_df.iloc[0]

# Metrics Row
m1, m2, m3, m4 = st.columns(4)

close_price = latest.get("Close", latest.get("close", 0))
start_price = first.get("Close", first.get("close", 0))
price_change = close_price - start_price
pct_change = (price_change / start_price) * 100

rsi = latest.get("RSI", 50)
if rsi > RSI_OVERBOUGHT:
    rsi_status = "Overbought"
    rsi_color = "#FF1744"
elif rsi < RSI_OVERSOLD:
    rsi_status = "Oversold"
    rsi_color = "#00C853"
else:
    rsi_status = "Neutral"
    rsi_color = "#A6ACCD"

signal = latest.get("Signal", "HOLD")
sig_color = "#00C853" if signal == "BUY" else "#FF1744" if signal == "SELL" else "#FFD600"

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Latest Price</div>
        <div class="metric-value">${close_price:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    change_color = "#00C853" if price_change >= 0 else "#FF1744"
    sign = "+" if price_change >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Period Return</div>
        <div class="metric-value" style="color: {change_color};">{sign}{price_change:.2f} ({sign}{pct_change:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">RSI (14)</div>
        <div class="metric-value" style="color: {rsi_color};">{rsi:.1f} <span style="font-size:16px;">{rsi_status}</span></div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Trading Signal</div>
        <div class="metric-value" style="color: {sig_color};">{signal}</div>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Interactive Charts", "Analysis Report", "Raw Data"])

with tab1:
    st.subheader("Complete Analysis Dashboard")
    st.markdown("Use the tools on the top right of the chart to zoom, pan, and save.")
    
    # Generate Plotly figure and display it directly
    fig = plot_full_dashboard(merged_df, selected_stock)
    # Streamlit natively renders plotly figures
    st.plotly_chart(fig, use_container_width=True, height=900)

with tab2:
    st.subheader("Automated Analysis Report")
    report_text = generate_stock_report(selected_stock, price_df, analysis_df)
    st.code(report_text, language="markdown")

with tab3:
    st.subheader("Historical Data")
    # Reset index to make Date a column
    display_df = merged_df.reset_index().sort_values("date", ascending=False)
    
    # Format columns for display
    format_dict = {
        'open': '{:.2f}', 'high': '{:.2f}', 'low': '{:.2f}', 'close': '{:.2f}',
        'Open': '{:.2f}', 'High': '{:.2f}', 'Low': '{:.2f}', 'Close': '{:.2f}',
        'Volume': '{:,}', 'volume': '{:,}',
        'SMA_20': '{:.2f}', 'SMA_50': '{:.2f}',
        'RSI': '{:.1f}', 'MACD': '{:.3f}'
    }
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("Developed by Nancy Nagpal - MCA Student - Batch 2024-2026")
