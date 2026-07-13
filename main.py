import sys
import os

# Add project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_STOCKS, CHARTS_DIR, REPORTS_DIR
from database import (initialize_database, insert_stock, insert_price_data,
                       insert_indicators, get_stock_data, get_indicators,
                       get_all_stocks, get_latest_price, get_stock_count)
from data_fetcher import (fetch_stock_data, fetch_company_info,
                           fetch_realtime_price, fetch_multiple_stocks)
from technical_analysis import run_full_analysis
from visualizer import (generate_all_charts, plot_comparison,
                         plot_candlestick, plot_full_dashboard)
from report_generator import (generate_stock_report, generate_comparison_report,
                                save_report, display_report)



def show_menu():
    """Display the main menu."""
    print("\n")
    print("╔══════════════════════════════════════════════════╗")
    print("║   Stock Market Data Analysis System              ║")
    print("╠══════════════════════════════════════════════════╣")
    print("║                                                  ║")
    print("║  1. Fetch & Store Stock Data                     ║")
    print("║  2. Run Technical Analysis                       ║")
    print("║  3. Generate Visualizations (Charts)             ║")
    print("║  4. View Analysis Report                         ║")
    print("║  5. Compare Multiple Stocks                      ║")
    print("║  6. Real-Time Price Check                        ║")
    print("║  7. Run Complete Pipeline (All Steps)            ║")
    print("║  8. View Database Status                         ║")
    print("║  0. Exit                                         ║")
    print("║                                                  ║")
    print("╚══════════════════════════════════════════════════╝")



def fetch_and_store():
    """Fetch stock data from API and store in SQLite database."""
    print("\n" + "=" * 50)
    print("  FETCHING & STORING STOCK DATA")
    print("=" * 50)
    
    print("\nChoose stocks to fetch:")
    print("  1. All default stocks (10 stocks)")
    print("  2. Enter a custom stock symbol")
    
    choice = input("\nYour choice (1/2): ").strip()
    
    if choice == "2":
        symbol = input("Enter stock symbol (e.g., AAPL, RELIANCE.NS): ").strip().upper()
        stocks = {symbol: symbol}
    else:
        stocks = DEFAULT_STOCKS
    
    for symbol, name in stocks.items():
        print(f"\n{'─' * 40}")
        print(f"Processing: {name} ({symbol})")
        
        # Fetch company info
        info = fetch_company_info(symbol)
        
        # Insert stock metadata into database
        stock_id = insert_stock(
            symbol=symbol,
            company_name=info["name"],
            sector=info["sector"],
            market_cap=info["market_cap"]
        )
        print(f"  Stock registered in DB (ID: {stock_id})")
        
        # Fetch price data from API
        df = fetch_stock_data(symbol, period="1y")
        
        if not df.empty:
            # Store price data in database
            rows = insert_price_data(stock_id, df)
            print(f"  Stored {rows} price records in database")
        else:
            print(f"  No data fetched for {symbol}")
    
    print("\nData fetching and storage complete!")



def run_analysis():
    """Run technical analysis on stored data."""
    print("\n" + "=" * 50)
    print("  RUNNING TECHNICAL ANALYSIS")
    print("=" * 50)
    
    stocks = get_all_stocks()
    if stocks.empty:
        print("  No stocks in database. Please fetch data first (Option 1).")
        return
    
    print(f"\n  Found {len(stocks)} stocks in database:")
    for _, row in stocks.iterrows():
        print(f"    • {row['symbol']} — {row['company_name']}")
    
    for _, row in stocks.iterrows():
        symbol = row["symbol"]
        stock_id = row["id"]
        print(f"\n{'─' * 40}")
        print(f"  Analyzing: {symbol}")
        
        # Get price data from database
        price_df = get_stock_data(symbol)
        
        if price_df.empty:
            print(f"  No price data for {symbol}")
            continue
        
        # Run technical analysis
        analysis_df = run_full_analysis(price_df)
        
        # Store indicators in database
        rows = insert_indicators(stock_id, analysis_df)
        print(f"  Stored {rows} indicator records")
    
    print("\nTechnical analysis complete for all stocks!")



def generate_charts():
    """Generate interactive Plotly charts."""
    print("\n" + "=" * 50)
    print("  GENERATING VISUALIZATIONS")
    print("=" * 50)
    
    stocks = get_all_stocks()
    if stocks.empty:
        print("  No stocks in database. Run Options 1 & 2 first.")
        return
    
    print("\nChoose chart generation mode:")
    print("  1. All charts for all stocks")
    print("  2. Dashboard for a specific stock")
    
    choice = input("\nYour choice (1/2): ").strip()
    
    if choice == "2":
        symbol = input("Enter symbol: ").strip().upper()
        price_df = get_stock_data(symbol)
        if price_df.empty:
            print(f"  No data found for {symbol}")
            return
        analysis_df = run_full_analysis(price_df)
        # Merge price and analysis data
        merged = price_df.join(analysis_df.drop(columns=[c for c in analysis_df.columns 
                               if c in price_df.columns], errors="ignore"))
        generate_all_charts(merged, symbol)
    else:
        for _, row in stocks.iterrows():
            symbol = row["symbol"]
            price_df = get_stock_data(symbol)
            if price_df.empty:
                continue
            analysis_df = run_full_analysis(price_df)
            merged = price_df.join(analysis_df.drop(columns=[c for c in analysis_df.columns 
                                   if c in price_df.columns], errors="ignore"))
            generate_all_charts(merged, symbol)
    
    print(f"\nCharts saved to: {CHARTS_DIR}")
    print("  💡 Open the .html files in your browser for interactive charts!")



def view_report():
    """Generate and display analysis report."""
    print("\n" + "=" * 50)
    print("  ANALYSIS REPORT")
    print("=" * 50)
    
    stocks = get_all_stocks()
    if stocks.empty:
        print("  No stocks in database. Run Options 1 & 2 first.")
        return
    
    print("\n  Available stocks:")
    for _, row in stocks.iterrows():
        print(f"    • {row['symbol']}")
    
    symbol = input("\nEnter symbol for report (or 'all'): ").strip().upper()
    
    if symbol == "ALL":
        for _, row in stocks.iterrows():
            sym = row["symbol"]
            price_df = get_stock_data(sym)
            analysis_df = run_full_analysis(price_df) if not price_df.empty else price_df
            report = generate_stock_report(sym, price_df, analysis_df)
            display_report(report)
            save_report(report, f"{sym}_report.txt")
    else:
        price_df = get_stock_data(symbol)
        if price_df.empty:
            print(f"  No data for {symbol}")
            return
        analysis_df = run_full_analysis(price_df)
        report = generate_stock_report(symbol, price_df, analysis_df)
        display_report(report)
        save_report(report, f"{symbol}_report.txt")



def compare_stocks():
    """Compare multiple stocks side by side."""
    print("\n" + "=" * 50)
    print("  MULTI-STOCK COMPARISON")
    print("=" * 50)
    
    stocks = get_all_stocks()
    if stocks.empty or len(stocks) < 2:
        print("  Need at least 2 stocks. Run Option 1 first.")
        return
    
    stock_data = {}
    analysis_data = {}
    
    for _, row in stocks.iterrows():
        symbol = row["symbol"]
        df = get_stock_data(symbol)
        if not df.empty:
            stock_data[symbol] = df
            analysis_data[symbol] = run_full_analysis(df)
    
    # Generate comparison chart
    plot_comparison(stock_data)
    
    # Generate comparison report
    report = generate_comparison_report(stock_data, analysis_data)
    display_report(report)
    save_report(report, "comparison_report.txt")
    
    print(f"\nComparison chart saved to: {CHARTS_DIR}")



def realtime_check():
    """Check real-time prices for stocks."""
    print("\n" + "=" * 50)
    print("  ⚡ REAL-TIME PRICE CHECK")
    print("=" * 50)
    
    symbol = input("\nEnter stock symbol (e.g., AAPL, RELIANCE.NS): ").strip().upper()
    
    print(f"\n  Fetching live data for {symbol}...")
    result = fetch_realtime_price(symbol)
    
    if result:
        print(f"\n  {'─' * 35}")
        print(f"  Symbol  : {result['symbol']}")
        print(f"  Price   : ₹/$ {result['price']:.2f}")
        print(f"  High    : ₹/$ {result['high']:.2f}")
        print(f"  Low     : ₹/$ {result['low']:.2f}")
        print(f"  Volume  : {result['volume']:,}")
        print(f"  Time    : {result['time']}")
        print(f"  {'─' * 35}")
    else:
        print(f"  Could not fetch price for {symbol}")



def run_complete_pipeline():
    """Run the entire pipeline: fetch → analyze → visualize → report."""
    print("\n" + "=" * 50)
    print("  🚀 RUNNING COMPLETE PIPELINE")
    print("=" * 50)
    
    # Step 1: Initialize database
    print("\nStep 1/5: Initializing database...")
    initialize_database()
    
    # Step 2: Fetch data
    print("\nStep 2/5: Fetching stock data...")
    for symbol, name in DEFAULT_STOCKS.items():
        print(f"\n  Processing: {name} ({symbol})")
        info = fetch_company_info(symbol)
        stock_id = insert_stock(symbol, info["name"], info["sector"], info["market_cap"])
        df = fetch_stock_data(symbol, period="1y")
        if not df.empty:
            insert_price_data(stock_id, df)
    
    # Step 3: Technical analysis
    print("\nStep 3/5: Running technical analysis...")
    stocks = get_all_stocks()
    stock_data = {}
    analysis_data = {}
    
    for _, row in stocks.iterrows():
        symbol = row["symbol"]
        stock_id = row["id"]
        price_df = get_stock_data(symbol)
        if not price_df.empty:
            analysis_df = run_full_analysis(price_df)
            insert_indicators(stock_id, analysis_df)
            stock_data[symbol] = price_df
            analysis_data[symbol] = analysis_df
    
    # Step 4: Generate charts
    print("\nStep 4/5: Generating charts...")
    for symbol in stock_data:
        price_df = stock_data[symbol]
        analysis_df = analysis_data[symbol]
        merged = price_df.join(analysis_df.drop(
            columns=[c for c in analysis_df.columns if c in price_df.columns],
            errors="ignore"))
        generate_all_charts(merged, symbol)
    
    if len(stock_data) > 1:
        plot_comparison(stock_data)
    
    # Step 5: Generate reports
    print("\nStep 5/5: Generating reports...")
    for symbol in stock_data:
        report = generate_stock_report(symbol, stock_data[symbol], analysis_data[symbol])
        save_report(report, f"{symbol}_report.txt")
    
    if len(stock_data) > 1:
        comp_report = generate_comparison_report(stock_data, analysis_data)
        save_report(comp_report, "comparison_report.txt")
    
    # Summary
    print("\n" + "=" * 50)
    print("  PIPELINE COMPLETE!")
    print("=" * 50)
    print(f"  Stocks analyzed : {len(stock_data)}")
    print(f"  Charts saved to : {CHARTS_DIR}")
    print(f"  Reports saved to: {REPORTS_DIR}")
    print(f"  Database stocks : {get_stock_count()}")
    print("\n  💡 Open .html files in charts/ folder for interactive charts!")



def database_status():
    """Show current database statistics."""
    print("\n" + "=" * 50)
    print("  DATABASE STATUS")
    print("=" * 50)
    
    try:
        stocks = get_all_stocks()
        print(f"\n  Total stocks: {len(stocks)}")
        
        if not stocks.empty:
            print(f"\n  {'Symbol':<15} {'Company':<30} {'Sector':<15}")
            print(f"  {'─' * 60}")
            for _, row in stocks.iterrows():
                print(f"  {row['symbol']:<15} {str(row['company_name'])[:28]:<30} {str(row['sector'])[:13]}")
            
            # Price data counts
            print(f"\n  Price records per stock:")
            from database import get_price_count
            for _, row in stocks.iterrows():
                count = get_price_count(row["symbol"])
                print(f"    {row['symbol']:<15} : {count} records")
    except Exception as e:
        print(f"  Database not initialized yet. Run Option 7 first.")
        print(f"     Error: {e}")



def main():
    """Main entry point — runs the interactive menu loop."""
    
    print("\n" + "🚀" * 25)
    print("  Welcome to the Stock Market Data Analysis System!")
    print("  Built with Python 🐍 + SQLite + Yahoo Finance API")
    print("🚀" * 25)
    
    # Initialize database on startup
    initialize_database()
    
    while True:
        show_menu()
        choice = input("\n  Enter your choice (0-8): ").strip()
        
        if choice == "1":
            fetch_and_store()
        elif choice == "2":
            run_analysis()
        elif choice == "3":
            generate_charts()
        elif choice == "4":
            view_report()
        elif choice == "5":
            compare_stocks()
        elif choice == "6":
            realtime_check()
        elif choice == "7":
            run_complete_pipeline()
        elif choice == "8":
            database_status()
        elif choice == "0":
            print("\n  👋 Goodbye! Happy Investing!\n")
            break
        else:
            print("\n  Invalid choice. Please enter 0-8.")
        
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
