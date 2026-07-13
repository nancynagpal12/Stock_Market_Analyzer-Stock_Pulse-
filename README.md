# 📈 Real-Time Stock Market Data Analysis System

A comprehensive Python-based stock market analysis platform that fetches live market data via API, stores it in a relational SQL database, performs technical analysis, and generates interactive visualizations.

## 📋 Abstract

This project implements an end-to-end stock market data analysis pipeline using Python, SQL, and financial APIs. The system fetches real-time and historical stock data from Yahoo Finance, stores it in a normalized SQLite relational database, calculates key technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands), generates interactive Plotly charts, and produces detailed analysis reports with automated trading signals. The modular architecture ensures maintainability, scalability, and clear separation of concerns.

## 🎯 Objectives

1. **Data Acquisition** — Fetch real-time stock market data using Yahoo Finance API (yfinance)
2. **Data Storage** — Design and implement a normalized relational database using SQLite with proper schema design
3. **Technical Analysis** — Calculate industry-standard financial indicators for market trend analysis
4. **Data Visualization** — Generate interactive, professional-grade charts using Plotly
5. **Report Generation** — Produce automated analysis reports with buy/sell trading signals
6. **Multi-Stock Comparison** — Enable comparative analysis across multiple stocks

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (Menu Interface)                 │
├──────────┬──────────┬───────────────┬──────────┬────────────────┤
│  config  │  data    │  technical    │  visual  │  report        │
│  .py     │  _fetcher│  _analysis    │  izer    │  _generator    │
│          │  .py     │  .py          │  .py     │  .py           │
│ Settings │ API Call │ SMA,RSI,MACD  │ Plotly   │ Text Reports   │
├──────────┴──────────┴───────────────┴──────────┴────────────────┤
│                    database.py (SQLite Layer)                    │
├─────────────────────────────────────────────────────────────────┤
│              data/stock_market.db (SQLite Database)             │
└─────────────────────────────────────────────────────────────────┘
```
## 📸 Screenshots
```
![Dashboard Screenshot](assets/Screenshot1.jpg)
```
### Data Flow
```
Yahoo Finance API → data_fetcher.py → database.py (SQLite)
                                           ↓
                                   technical_analysis.py
                                     ↓            ↓
                              visualizer.py   report_generator.py
                              (HTML Charts)    (Text Reports)
```

## 🗄️ Database Schema (ER Diagram)

```
┌────────────────┐       ┌──────────────────────┐
│    stocks      │       │    stock_prices       │
├────────────────┤       ├──────────────────────┤
│ id (PK)        │──1:N──│ id (PK)              │
│ symbol (UNIQUE)│       │ stock_id (FK)         │
│ company_name   │       │ date                  │
│ sector         │       │ open, high, low       │
│ market_cap     │       │ close, adj_close      │
│ added_date     │       │ volume                │
└────────────────┘       └──────────────────────┘
        │
        │                ┌──────────────────────┐
        │                │ technical_indicators  │
        │                ├──────────────────────┤
        └───────1:N──────│ id (PK)              │
                         │ stock_id (FK)         │
                         │ date                  │
                         │ sma_20, sma_50        │
                         │ ema_12, ema_26        │
                         │ rsi, macd             │
                         │ signal_line           │
                         │ bollinger_upper/lower │
                         │ daily_return, signal  │
                         └──────────────────────┘
```

## 🛠️ Technologies Used

| Technology | Purpose | Version |
|---|---|---|
| **Python** | Core programming language | 3.8+ |
| **SQLite** | Relational database (built into Python) | 3.x |
| **yfinance** | Yahoo Finance API wrapper | 0.2+ |
| **pandas** | Data manipulation & analysis | 2.0+ |
| **Plotly** | Interactive chart generation | 5.0+ |
| **kaleido** | Static chart image export | 0.2+ |

## 📁 Project Structure

```
StockMarketAnalyzer/
├── config.py              # Configuration settings (symbols, paths, parameters)
├── database.py            # SQLite database operations (CRUD)
├── data_fetcher.py        # Yahoo Finance API data fetching
├── technical_analysis.py  # Technical indicator calculations
├── visualizer.py          # Interactive Plotly chart generation
├── report_generator.py    # Analysis report generation
├── main.py                # Main entry point (menu-driven interface)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── data/                  # SQLite database file
│   └── stock_market.db
├── charts/                # Generated interactive charts (HTML + PNG)
└── reports/               # Generated analysis reports (TXT)
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for API data fetching)

### Step 1: Install Dependencies
```bash
cd StockMarketAnalyzer
pip install -r requirements.txt
```

### Step 2: Run the Program
```bash
python main.py
```

### Step 3: Use the Menu
Select **Option 7** to run the complete pipeline (recommended for first run), or use individual options:

```
╔══════════════════════════════════════════════════╗
║   📈 Stock Market Data Analysis System          ║
╠══════════════════════════════════════════════════╣
║  1. Fetch & Store Stock Data                     ║
║  2. Run Technical Analysis                       ║
║  3. Generate Visualizations (Charts)             ║
║  4. View Analysis Report                         ║
║  5. Compare Multiple Stocks                      ║
║  6. Real-Time Price Check                        ║
║  7. Run Complete Pipeline (All Steps)            ║
║  8. View Database Status                         ║
║  0. Exit                                         ║
╚══════════════════════════════════════════════════╝
```

## 📊 Technical Indicators Explained

| Indicator | Full Name | Description |
|---|---|---|
| **SMA** | Simple Moving Average | Average closing price over N days. SMA(20) and SMA(50) are used. |
| **EMA** | Exponential Moving Average | Weighted average giving more importance to recent prices. |
| **RSI** | Relative Strength Index | Momentum oscillator (0-100). Above 70 = overbought, below 30 = oversold. |
| **MACD** | Moving Average Convergence Divergence | Trend-following momentum indicator. Buy when MACD crosses above signal line. |
| **Bollinger Bands** | — | Volatility bands around SMA. Price near upper band = overbought. |

## 📈 Output Samples

### Charts Generated (per stock):
1. **Candlestick Chart** — OHLC price with volume
2. **Moving Averages** — SMA/EMA overlay on price
3. **RSI Chart** — With overbought/oversold zones
4. **MACD Chart** — MACD line, signal line, histogram
5. **Bollinger Bands** — Price with volatility bands
6. **Full Dashboard** — All indicators in one view
7. **Multi-Stock Comparison** — Normalized price comparison

### Reports Generated:
- Individual stock analysis reports (`.txt`)
- Multi-stock comparison report with rankings

## 🔮 Future Scope

1. **Machine Learning** — Implement LSTM/Random Forest for price prediction
2. **Web Dashboard** — Build interactive web interface using Streamlit or Flask
3. **Portfolio Optimization** — Markowitz Mean-Variance optimization
4. **Sentiment Analysis** — Analyze news headlines for market sentiment
5. **Automated Trading** — Paper trading simulation with backtesting
6. **Cloud Deployment** — Deploy on AWS/GCP for 24/7 operation

## 👨‍💻 How to Modify

- **Change stocks**: Edit `DEFAULT_STOCKS` dictionary in `config.py`
- **Change date range**: Modify `LOOKBACK_DAYS` in `config.py`
- **Change indicators**: Adjust `SMA_SHORT_WINDOW`, `RSI_PERIOD`, etc. in `config.py`
- **Change chart theme**: Set `CHART_THEME` in `config.py`

## 📝 License

This project is developed for educational and research purposes.
