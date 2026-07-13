import os
from datetime import datetime, timedelta


# Get the folder where this config.py file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database file path  →  data/stock_market.db
DATABASE_PATH = os.path.join(BASE_DIR, "data", "stock_market.db")

# Folder to save generated charts
CHARTS_DIR = os.path.join(BASE_DIR, "charts")

# Folder to save analysis reports
REPORTS_DIR = os.path.join(BASE_DIR, "reports")



# Indian NSE Stocks (append .NS for Yahoo Finance)
INDIAN_STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "WIPRO.NS": "Wipro",
}

# US Stocks
US_STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet (Google)",
    "MSFT": "Microsoft",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
}

# Combined — this is the default list used by the program
DEFAULT_STOCKS = {**INDIAN_STOCKS, **US_STOCKS}



# How far back to fetch data (in days)
LOOKBACK_DAYS = 365

# Calculated start and end dates
END_DATE = datetime.today().strftime("%Y-%m-%d")        # Today
START_DATE = (datetime.today() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

# Alternative: fetch by period string (used in some functions)
# Options: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"
DEFAULT_PERIOD = "1y"



# Simple Moving Average (SMA) windows
SMA_SHORT_WINDOW = 20    # 20-day SMA (short-term trend)
SMA_LONG_WINDOW = 50     # 50-day SMA (long-term trend)

# Exponential Moving Average (EMA) spans
EMA_SHORT_SPAN = 12      # 12-day EMA (used in MACD)
EMA_LONG_SPAN = 26       # 26-day EMA (used in MACD)

# MACD Signal Line
MACD_SIGNAL_SPAN = 9     # 9-day EMA of MACD

# Relative Strength Index (RSI)
RSI_PERIOD = 14           # Standard 14-day RSI
RSI_OVERBOUGHT = 70       # RSI above 70 = overbought (may fall)
RSI_OVERSOLD = 30         # RSI below 30 = oversold (may rise)

# Bollinger Bands
BOLLINGER_WINDOW = 20     # 20-day window
BOLLINGER_STD_DEV = 2     # 2 standard deviations



# Chart color theme
CHART_THEME = "plotly_dark"    # Dark theme for professional look
# Options: "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"

# Chart dimensions
CHART_WIDTH = 1200
CHART_HEIGHT = 700

# Colors for charts
COLOR_BULLISH = "#00C853"      # Green — price going up
COLOR_BEARISH = "#FF1744"      # Red — price going down
COLOR_SMA_SHORT = "#FFD600"    # Yellow — short-term SMA line
COLOR_SMA_LONG = "#2979FF"     # Blue — long-term SMA line
COLOR_BOLLINGER = "#AB47BC"    # Purple — Bollinger Bands
