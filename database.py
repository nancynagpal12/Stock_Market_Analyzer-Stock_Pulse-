import sqlite3
import math
import pandas as pd
from config import DATABASE_PATH


def get_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create all required tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            company_name TEXT,
            sector TEXT,
            market_cap TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            date DATE NOT NULL,
            open REAL, high REAL, low REAL,
            close REAL, adj_close REAL, volume INTEGER,
            FOREIGN KEY (stock_id) REFERENCES stocks(id),
            UNIQUE(stock_id, date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            date DATE NOT NULL,
            sma_20 REAL, sma_50 REAL,
            ema_12 REAL, ema_26 REAL,
            rsi REAL, macd REAL,
            signal_line REAL, macd_histogram REAL,
            bollinger_upper REAL, bollinger_middle REAL, bollinger_lower REAL,
            daily_return REAL, signal TEXT,
            FOREIGN KEY (stock_id) REFERENCES stocks(id),
            UNIQUE(stock_id, date)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_sd ON stock_prices(stock_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ind_sd ON technical_indicators(stock_id, date)")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def safe_float(value):
    """Safely convert a value to float, returning None for NaN/None."""
    try:
        f = float(value)
        return None if math.isnan(f) else round(f, 4)
    except (ValueError, TypeError):
        return None


def insert_stock(symbol, company_name="", sector="", market_cap=""):
    """Add a stock's metadata to the stocks table. Returns the stock's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO stocks (symbol, company_name, sector, market_cap) VALUES (?, ?, ?, ?)",
        (symbol, company_name, sector, market_cap))
    conn.commit()
    cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
    stock_id = cursor.fetchone()[0]
    conn.close()
    return stock_id


def insert_price_data(stock_id, df):
    """Insert daily price data from a DataFrame into stock_prices table."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = 0
    for date, row in df.iterrows():
        try:
            date_str = pd.Timestamp(date).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT OR REPLACE INTO stock_prices 
                (stock_id, date, open, high, low, close, adj_close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, date_str,
                  round(float(row.get("Open", 0)), 2),
                  round(float(row.get("High", 0)), 2),
                  round(float(row.get("Low", 0)), 2),
                  round(float(row.get("Close", 0)), 2),
                  round(float(row.get("Adj Close", row.get("Close", 0))), 2),
                  int(row.get("Volume", 0))))
            rows += 1
        except Exception as e:
            print(f"  Skipped row {date}: {e}")
    conn.commit()
    conn.close()
    return rows


def insert_indicators(stock_id, df):
    """Insert calculated technical indicators into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = 0
    for date, row in df.iterrows():
        try:
            date_str = pd.Timestamp(date).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT OR REPLACE INTO technical_indicators
                (stock_id, date, sma_20, sma_50, ema_12, ema_26, rsi,
                 macd, signal_line, macd_histogram,
                 bollinger_upper, bollinger_middle, bollinger_lower,
                 daily_return, signal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, date_str,
                  safe_float(row.get("SMA_20")), safe_float(row.get("SMA_50")),
                  safe_float(row.get("EMA_12")), safe_float(row.get("EMA_26")),
                  safe_float(row.get("RSI")), safe_float(row.get("MACD")),
                  safe_float(row.get("Signal_Line")), safe_float(row.get("MACD_Histogram")),
                  safe_float(row.get("Bollinger_Upper")), safe_float(row.get("Bollinger_Middle")),
                  safe_float(row.get("Bollinger_Lower")), safe_float(row.get("Daily_Return")),
                  str(row.get("Signal", "HOLD"))))
            rows += 1
        except Exception as e:
            print(f"  Skipped indicator {date}: {e}")
    conn.commit()
    conn.close()
    return rows


def get_stock_data(symbol, start_date=None, end_date=None):
    """Retrieve price data for a stock from the database."""
    conn = get_connection()
    query = """
        SELECT sp.date, sp.open, sp.high, sp.low, sp.close, sp.adj_close, sp.volume
        FROM stock_prices sp JOIN stocks s ON sp.stock_id = s.id
        WHERE s.symbol = ?
    """
    params = [symbol]
    if start_date:
        query += " AND sp.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND sp.date <= ?"
        params.append(end_date)
    query += " ORDER BY sp.date ASC"
    df = pd.read_sql_query(query, conn, params=params, index_col="date", parse_dates=["date"])
    conn.close()
    return df


def get_indicators(symbol, start_date=None, end_date=None):
    """Retrieve technical indicators for a stock from the database."""
    conn = get_connection()
    query = """
        SELECT ti.* FROM technical_indicators ti
        JOIN stocks s ON ti.stock_id = s.id WHERE s.symbol = ?
    """
    params = [symbol]
    if start_date:
        query += " AND ti.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND ti.date <= ?"
        params.append(end_date)
    query += " ORDER BY ti.date ASC"
    df = pd.read_sql_query(query, conn, params=params, index_col="date", parse_dates=["date"])
    conn.close()
    return df


def get_all_stocks():
    """Get a list of all stocks stored in the database."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM stocks ORDER BY symbol", conn)
    conn.close()
    return df


def get_latest_price(symbol):
    """Get the most recent price data for a stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.date, sp.open, sp.high, sp.low, sp.close, sp.volume
        FROM stock_prices sp JOIN stocks s ON sp.stock_id = s.id
        WHERE s.symbol = ? ORDER BY sp.date DESC LIMIT 1
    """, (symbol,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"date": row[0], "open": row[1], "high": row[2],
                "low": row[3], "close": row[4], "volume": row[5]}
    return None


def get_stock_count():
    """Get total number of stocks in database."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM stocks")
    count = c.fetchone()[0]
    conn.close()
    return count


def get_price_count(symbol):
    """Get total number of price records for a stock."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM stock_prices sp JOIN stocks s ON sp.stock_id = s.id WHERE s.symbol = ?", (symbol,))
    count = c.fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    print("Setting up database...")
    initialize_database()
    print(f"Database location: {DATABASE_PATH}")
