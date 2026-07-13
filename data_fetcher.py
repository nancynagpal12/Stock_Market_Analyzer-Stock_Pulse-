import yfinance as yf
import pandas as pd
from config import DEFAULT_STOCKS, START_DATE, END_DATE, DEFAULT_PERIOD


def fetch_stock_data(symbol, start=None, end=None, period=None):

    try:
        print(f"  Fetching data for {symbol}...")
        ticker = yf.Ticker(symbol)
        
        if period:
            df = ticker.history(period=period)
        else:
            s = start or START_DATE
            e = end or END_DATE
            df = ticker.history(start=s, end=e)
        
        if df.empty:
            print(f"  No data returned for {symbol}")
            return pd.DataFrame()
        
        # Clean column names (remove multi-level if present)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Keep only the columns we need
        keep_cols = ["Open", "High", "Low", "Close", "Volume"]
        available = [c for c in keep_cols if c in df.columns]
        df = df[available]
        
        # Add Adj Close (same as Close for yfinance history)
        if "Adj Close" not in df.columns:
            df["Adj Close"] = df["Close"]
        
        print(f"  Got {len(df)} records for {symbol}")
        return df
        
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return pd.DataFrame()


def fetch_company_info(symbol):

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "name": info.get("longName", info.get("shortName", symbol)),
            "sector": info.get("sector", "N/A"),
            "market_cap": str(info.get("marketCap", "N/A"))
        }
    except Exception:
        return {"name": symbol, "sector": "N/A", "market_cap": "N/A"}


def fetch_realtime_price(symbol):

    try:
        ticker = yf.Ticker(symbol)
        # Get latest 1-day data with 1-minute intervals
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty:
            # Fallback: get last closing price
            df = ticker.history(period="5d")
            if df.empty:
                return None
        
        latest = df.iloc[-1]
        return {
            "symbol": symbol,
            "price": round(float(latest["Close"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "time": str(df.index[-1])
        }
    except Exception as e:
        print(f"  Error getting realtime price for {symbol}: {e}")
        return None


def fetch_multiple_stocks(symbols=None, period=None):

    if symbols is None:
        symbols = DEFAULT_STOCKS
    
    p = period or DEFAULT_PERIOD
    results = {}
    total = len(symbols)
    
    print(f"\nFetching data for {total} stocks...\n")
    
    for i, (symbol, name) in enumerate(symbols.items(), 1):
        print(f"[{i}/{total}] {name} ({symbol})")
        df = fetch_stock_data(symbol, period=p)
        if not df.empty:
            results[symbol] = df
    
    print(f"\nSuccessfully fetched data for {len(results)}/{total} stocks\n")
    return results


if __name__ == "__main__":
    # Quick test — fetch Apple data
    print("Testing data fetcher...")
    data = fetch_stock_data("AAPL", period="1mo")
    if not data.empty:
        print(data.head())
        print(f"\nTotal records: {len(data)}")
    
    info = fetch_company_info("AAPL")
    print(f"\nCompany Info: {info}")
