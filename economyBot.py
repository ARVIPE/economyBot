import yfinance as yf
import pandas as pd
import time

def calculate_rsi(data, period=14):
    delta = data.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    exp12 = data.ewm(span=12, adjust=False).mean()
    exp26 = data.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

tickers = ["AAPL", "MSFT", "NVDA", "GOOGL"]  # Add your full list of tickers

while True:  # Infinite loop to run every 15 minutes
    rsi_signals = {}

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.history(period="50d")

        if data.empty:
            continue

        data["RSI"] = calculate_rsi(data["Close"])
        data["MACD"], data["MACD_Signal"] = calculate_macd(data["Close"])

        latest_rsi = data["RSI"].dropna().iloc[-1]
        latest_macd = data["MACD"].iloc[-1]
        latest_macd_signal = data["MACD_Signal"].iloc[-1]

        data["50_MA"] = data["Close"].rolling(window=50).mean()
        data["200_MA"] = data["Close"].rolling(window=200).mean()
        latest_50_ma = data["50_MA"].iloc[-1]
        latest_200_ma = data["200_MA"].iloc[-1]

        data["Volume_Avg"] = data["Volume"].rolling(window=20).mean()
        latest_volume = data["Volume"].iloc[-1]
        latest_avg_volume = data["Volume_Avg"].iloc[-1]

        volume_surge = latest_volume > 1.5 * latest_avg_volume
        support_level = data["Close"].min()
        near_support = data["Close"].iloc[-1] <= support_level * 1.05

        if latest_rsi < 30:
            signal = "BUY (Oversold)"
            if latest_macd > latest_macd_signal:
                signal += " - MACD Bullish Crossover"
            if data["Close"].iloc[-1] > latest_50_ma and data["Close"].iloc[-1] > latest_200_ma:
                signal += " - Above MAs"
            if volume_surge:
                signal += " - Volume Surge"
            if near_support:
                signal += " - Near Support Level"
        elif latest_rsi > 70:
            signal = "SELL (Overbought)"
        else:
            signal = "NEUTRAL (Stable)"

        rsi_signals[ticker] = {
            "RSI": round(latest_rsi, 2),
            "Signal": signal,
            "Price": round(data["Close"].iloc[-1], 2),
            "50_MA": round(latest_50_ma, 2),
            "200_MA": round(latest_200_ma, 2),
            "Volume": latest_volume,
            "Avg_Volume": latest_avg_volume,
            "MACD": round(latest_macd, 2),
            "MACD_Signal": round(latest_macd_signal, 2),
        }

    rsi_df = pd.DataFrame.from_dict(rsi_signals, orient="index")
    print(rsi_df)

    # Wait 15 minutes before running again
    print("Waiting 15 minutes...")
    time.sleep(900)  # 900 seconds = 15 minutes
