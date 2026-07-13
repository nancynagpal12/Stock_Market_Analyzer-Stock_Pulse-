"""
╔══════════════════════════════════════════════════════════════╗
║              REPORT GENERATOR                               ║
║  Creates text-based analysis summary reports.               ║
║  Reports are saved in the reports/ folder.                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
from datetime import datetime
import pandas as pd
from config import REPORTS_DIR, RSI_OVERBOUGHT, RSI_OVERSOLD


def generate_stock_report(symbol, price_df, analysis_df):
    """
    Generate a detailed analysis report for a single stock.
    
    Args:
        symbol: Stock ticker
        price_df: DataFrame with price data
        analysis_df: DataFrame with technical indicators
    
    Returns:
        str: The complete report text
    """
    close_col = "Close" if "Close" in price_df.columns else "close"
    
    report = []
    report.append("=" * 60)
    report.append(f"  STOCK ANALYSIS REPORT — {symbol}")
    report.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    report.append("\nPRICE SUMMARY")
    report.append("-" * 40)
    if not price_df.empty:
        close = price_df[close_col]
        report.append(f"  Period        : {price_df.index[0].strftime('%Y-%m-%d')} to {price_df.index[-1].strftime('%Y-%m-%d')}")
        report.append(f"  Total Records : {len(price_df)}")
        report.append(f"  Latest Close  : ₹/$ {close.iloc[-1]:.2f}")
        report.append(f"  Highest Price : ₹/$ {close.max():.2f}")
        report.append(f"  Lowest Price  : ₹/$ {close.min():.2f}")
        report.append(f"  Average Price : ₹/$ {close.mean():.2f}")
        report.append(f"  Std Deviation : {close.std():.2f}")
        
        change = close.iloc[-1] - close.iloc[0]
        change_pct = (change / close.iloc[0]) * 100
        direction = "UP" if change > 0 else "DOWN"
        report.append(f"  Price Change  : {change:+.2f} ({change_pct:+.2f}%) {direction}")
    
    report.append("\nTECHNICAL INDICATORS (Latest)")
    report.append("-" * 40)
    if not analysis_df.empty:
        latest = analysis_df.iloc[-1]
        
        if "SMA_20" in analysis_df.columns and pd.notna(latest.get("SMA_20")):
            report.append(f"  SMA (20-day)  : {latest['SMA_20']:.2f}")
        if "SMA_50" in analysis_df.columns and pd.notna(latest.get("SMA_50")):
            report.append(f"  SMA (50-day)  : {latest['SMA_50']:.2f}")
        if "EMA_12" in analysis_df.columns and pd.notna(latest.get("EMA_12")):
            report.append(f"  EMA (12-day)  : {latest['EMA_12']:.2f}")
        if "EMA_26" in analysis_df.columns and pd.notna(latest.get("EMA_26")):
            report.append(f"  EMA (26-day)  : {latest['EMA_26']:.2f}")
        
        if "RSI" in analysis_df.columns and pd.notna(latest.get("RSI")):
            rsi_val = latest["RSI"]
            rsi_status = "OVERBOUGHT" if rsi_val > RSI_OVERBOUGHT else \
                         "OVERSOLD" if rsi_val < RSI_OVERSOLD else "NEUTRAL"
            report.append(f"  RSI (14-day)  : {rsi_val:.2f} → {rsi_status}")
        
        if "MACD" in analysis_df.columns and pd.notna(latest.get("MACD")):
            report.append(f"  MACD          : {latest['MACD']:.4f}")
            report.append(f"  Signal Line   : {latest['Signal_Line']:.4f}")
            macd_status = "BULLISH" if latest["MACD"] > latest["Signal_Line"] else "BEARISH"
            report.append(f"  MACD Status   : {macd_status}")
        
        if "Bollinger_Upper" in analysis_df.columns and pd.notna(latest.get("Bollinger_Upper")):
            report.append(f"  Bollinger Up  : {latest['Bollinger_Upper']:.2f}")
            report.append(f"  Bollinger Low : {latest['Bollinger_Lower']:.2f}")
    
    report.append("\nTRADING SIGNALS SUMMARY")
    report.append("-" * 40)
    if "Signal" in analysis_df.columns:
        signal_counts = analysis_df["Signal"].value_counts()
        for sig, count in signal_counts.items():
            report.append(f"  {sig:6s} : {count} days")
        
        latest_signal = analysis_df["Signal"].iloc[-1]
        report.append(f"\n  Latest Signal: {latest_signal}")
    
    report.append("\nDAILY RETURNS STATISTICS")
    report.append("-" * 40)
    if "Daily_Return" in analysis_df.columns:
        returns = analysis_df["Daily_Return"].dropna()
        report.append(f"  Average Return : {returns.mean():.4f}%")
        report.append(f"  Best Day       : {returns.max():.4f}%")
        report.append(f"  Worst Day      : {returns.min():.4f}%")
        report.append(f"  Volatility     : {returns.std():.4f}%")
        positive_days = (returns > 0).sum()
        total_days = len(returns)
        report.append(f"  Positive Days  : {positive_days}/{total_days} ({positive_days/total_days*100:.1f}%)")
    
    report.append("\n" + "=" * 60)
    report.append("  END OF REPORT")
    report.append("=" * 60)
    
    return "\n".join(report)


def generate_comparison_report(stock_data_dict, analysis_dict):
    """
    Generate a comparison report for multiple stocks.
    
    Args:
        stock_data_dict: {symbol: price_df}
        analysis_dict: {symbol: analysis_df}
    
    Returns:
        str: Comparison report text
    """
    report = []
    report.append("=" * 60)
    report.append("  MULTI-STOCK COMPARISON REPORT")
    report.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    rows = []
    for symbol in stock_data_dict:
        df = stock_data_dict[symbol]
        close_col = "Close" if "Close" in df.columns else "close"
        if df.empty:
            continue
        close = df[close_col]
        change_pct = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100
        
        latest_rsi = None
        latest_signal = "N/A"
        if symbol in analysis_dict and not analysis_dict[symbol].empty:
            adf = analysis_dict[symbol]
            if "RSI" in adf.columns:
                latest_rsi = adf["RSI"].iloc[-1]
            if "Signal" in adf.columns:
                latest_signal = adf["Signal"].iloc[-1]
        
        rows.append({
            "Symbol": symbol,
            "Latest": f"{close.iloc[-1]:.2f}",
            "Change%": f"{change_pct:+.2f}%",
            "RSI": f"{latest_rsi:.1f}" if latest_rsi and pd.notna(latest_rsi) else "N/A",
            "Signal": latest_signal
        })
    
    rows.sort(key=lambda x: float(x["Change%"].replace("%", "").replace("+", "")), reverse=True)
    
    report.append(f"\n{'Symbol':<15} {'Price':>10} {'Change':>10} {'RSI':>8} {'Signal':>8}")
    report.append("-" * 55)
    for r in rows:
        report.append(f"  {r['Symbol']:<13} {r['Latest']:>10} {r['Change%']:>10} {r['RSI']:>8} {r['Signal']:>8}")
    
    report.append("\nRANKINGS")
    report.append("-" * 40)
    if rows:
        report.append(f"  Top Gainer  : {rows[0]['Symbol']} ({rows[0]['Change%']})")
        report.append(f"  Top Loser   : {rows[-1]['Symbol']} ({rows[-1]['Change%']})")
    
    report.append("\n" + "=" * 60)
    return "\n".join(report)


def save_report(report_text, filename):
    """Save report text to a file in the reports directory."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"  Report saved: {filepath}")
    return filepath


def display_report(report_text):
    """Print the report to the console."""
    print(report_text)
