import pandas as pd
from config import (SMA_SHORT_WINDOW, SMA_LONG_WINDOW,
                    EMA_SHORT_SPAN, EMA_LONG_SPAN, MACD_SIGNAL_SPAN,
                    RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
                    BOLLINGER_WINDOW, BOLLINGER_STD_DEV)



def calculate_sma(data, window):

    return data.rolling(window=window).mean()


def calculate_ema(data, span):

    return data.ewm(span=span, adjust=False).mean()



def calculate_rsi(data, period=None):

    if period is None:
        period = RSI_PERIOD

    # Step 1: Daily price changes
    delta = data.diff()

    # Step 2: Separate gains and losses
    gain = delta.where(delta > 0, 0.0)   # Keep only positive changes
    loss = -delta.where(delta < 0, 0.0)  # Keep only negative (make positive)

    # Step 3: Average gains and losses (using EMA for smoothing)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    # Step 4: Calculate RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi



def calculate_macd(data):

    ema_short = calculate_ema(data, EMA_SHORT_SPAN)   # 12-day EMA
    ema_long = calculate_ema(data, EMA_LONG_SPAN)     # 26-day EMA

    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=MACD_SIGNAL_SPAN, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram



def calculate_bollinger_bands(data, window=None, num_std=None):

    if window is None:
        window = BOLLINGER_WINDOW
    if num_std is None:
        num_std = BOLLINGER_STD_DEV

    middle = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)

    return upper, middle, lower



def calculate_daily_returns(data):

    return data.pct_change() * 100



def generate_signals(df):

    signals = pd.Series("HOLD", index=df.index)

    for i in range(1, len(df)):
        rsi = df["RSI"].iloc[i]
        macd = df["MACD"].iloc[i]
        signal = df["Signal_Line"].iloc[i]
        macd_prev = df["MACD"].iloc[i - 1]
        signal_prev = df["Signal_Line"].iloc[i - 1]

        # Check for NaN values
        if pd.isna(rsi) or pd.isna(macd) or pd.isna(signal):
            continue

        # BUY conditions
        if rsi < RSI_OVERSOLD:
            signals.iloc[i] = "BUY"
        elif macd_prev < signal_prev and macd > signal:
            signals.iloc[i] = "BUY"
        # SELL conditions
        elif rsi > RSI_OVERBOUGHT:
            signals.iloc[i] = "SELL"
        elif macd_prev > signal_prev and macd < signal:
            signals.iloc[i] = "SELL"

    return signals



def run_full_analysis(df):

    # Make a copy to avoid modifying the original
    result = df.copy()
    close = result["Close"] if "Close" in result.columns else result["close"]

    # Moving Averages
    result["SMA_20"] = calculate_sma(close, SMA_SHORT_WINDOW)
    result["SMA_50"] = calculate_sma(close, SMA_LONG_WINDOW)
    result["EMA_12"] = calculate_ema(close, EMA_SHORT_SPAN)
    result["EMA_26"] = calculate_ema(close, EMA_LONG_SPAN)

    # RSI
    result["RSI"] = calculate_rsi(close)

    # MACD
    macd, signal, histogram = calculate_macd(close)
    result["MACD"] = macd
    result["Signal_Line"] = signal
    result["MACD_Histogram"] = histogram

    # Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(close)
    result["Bollinger_Upper"] = upper
    result["Bollinger_Middle"] = middle
    result["Bollinger_Lower"] = lower

    # Daily Returns
    result["Daily_Return"] = calculate_daily_returns(close)

    # Trading Signals
    result["Signal"] = generate_signals(result)

    print(f"  Analysis complete — {len(result)} data points processed")
    return result


if __name__ == "__main__":
    # Quick test with sample data
    print("Testing technical analysis...")
    import numpy as np
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    prices = pd.Series(np.cumsum(np.random.randn(100)) + 100, index=dates)
    test_df = pd.DataFrame({"Close": prices})
    result = run_full_analysis(test_df)
    print(result.tail())
