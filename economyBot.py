import yfinance as yf
import pandas as pd

def calculate_rsi(data, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    delta = data.diff(1)  # Calculate daily price changes

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()  # Average gain over the period
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  # Average loss over the period

    rs = gain / loss  # Relative strength
    rsi = 100 - (100 / (1 + rs))  # RSI formula

    return rsi

def calculate_macd(data):
    """Calculate the Moving Average Convergence Divergence (MACD)."""
    exp12 = data.ewm(span=12, adjust=False).mean()
    exp26 = data.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal


# List of stock tickers to analyze
tickers = [
    # Big Tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "ADBE", "AMD", "ASML", "SHOP", "SNOW", "PLTR", "COIN", "MSTR", "T", "CRM", "INTC", "IBM", "ORCL", "UBER", "LYFT", "SQ", "TWLO", "PANW", "CSCO", "DELL", "ZM", "DDOG", "DOCU",

    # Finance
    "JPM", "V", "MA", "PYPL", "GS", "MS", "BAC", "C", "WFC", "AXP", "BLK", "SCHW", "RY", "TD", "BNS", "TFC", "USB", "PGR", "AIG", "MET", "PRU", "HIG",

    # Energy
    "XOM", "CVX", "COP", "NEE", "BP", "SHEL", "OXY", "PSX", "VLO", "MPC", "SLB", "HAL", "BKR", "ENB", "KMI", "ET", "TRP", "WMB",

    # Healthcare
    "JNJ", "PFE", "MRNA", "LLY", "UNH", "BNTX", "ABT", "ABBV", "GILD", "BIIB", "REGN", "VRTX", "DHR", "TMO", "SYK", "ISRG", "ZBH", "EW", "CVS", "CI", "HUM", "ELV", "MDT", "BMY", "AMGN",

    # Consumer Goods
    "KO", "PEP", "MCD", "NKE", "PG", "HD", "SBUX", "COST", "WMT", "TGT", "LOW", "DG", "DLTR", "TJX", "ROST", "YUM", "DPZ", "WBA", "CVNA", "BBY", "DASH", "CHWY", "LULU", "RCL", "CCL", "MAR", "HLT", "SBUX", "TSLA", "F", "GM", "HOG",

    # Industrials
    "TM", "GE", "HON", "UPS", "FDX", "CAT", "DE", "BA", "LMT", "NOC", "GD", "RTX", "TDG", "CSX", "NSC", "UNP", "CP", "CNI", "EMR", "ITW", "PH", "MMM", "NKE",

    # Real Estate (REITs)
    "O", "AMT", "PLD", "SPG", "EQIX", "VICI", "PSA", "DLR", "CCI", "AVB", "EQR", "WY", "EXR", "STAG", "MAA",

    # International Stocks
    "TSM", "BABA", "NSRGY", "NVS", "RIO", "BP", "SHEL", "SAN", "HDB", "INFY", "TCEHY", "NTES", "JD", "SE", "MELI", "BHP", "VALE", "TM", "SONY", "LVMUY", "ASML", "SAP", "RACE", "VWAGY", "SMFG", "BBVA", "UBS", "DB", "ING",

    # ETFs
    "SPY", "QQQ", "VTI", "VOO", "SCHD", "EEM", "VIG", "ARKK", "DIA", "IWM", "IVV", "VT", "VGT", "XLK", "XLF", "XLY", "XLV", "XLE", "XLI", "XLU", "XLC", "XLB", "XLP", "XLRE", "ARKG", "ARKW", "SOXX", "SMH"
]


# Dictionary to store stock classification
rsi_signals = {}

# Fetch and analyze RSI for each stock
for ticker in tickers:
    stock = yf.Ticker(ticker)
    data = stock.history(period="50d")  # Get last 50 days of data

    if data.empty:
        continue  # Skip if no data is available

    # Calculate RSI
    data["RSI"] = calculate_rsi(data["Close"])

    # Calculate MACD
    data["MACD"], data["MACD_Signal"] = calculate_macd(data["Close"])

    # Get the latest RSI value
    latest_rsi = data["RSI"].dropna().iloc[-1]  # Drop NaN values and get last RSI

    # Get the latest MACD values
    latest_macd = data["MACD"].iloc[-1]
    latest_macd_signal = data["MACD_Signal"].iloc[-1]

    # Check Moving Averages (50-day and 200-day)
    data["50_MA"] = data["Close"].rolling(window=50).mean()
    data["200_MA"] = data["Close"].rolling(window=200).mean()
    latest_50_ma = data["50_MA"].iloc[-1]
    latest_200_ma = data["200_MA"].iloc[-1]

    # Check Volume Surge (Volume over 20-day average)
    data["Volume_Avg"] = data["Volume"].rolling(window=20).mean()
    latest_volume = data["Volume"].iloc[-1]
    latest_avg_volume = data["Volume_Avg"].iloc[-1]
    volume_surge = latest_volume > 1.5 * latest_avg_volume  # 50% surge in volume

    # Check price action (if near recent support level)
    support_level = data["Close"].min()  # Simplified support level (could use more advanced methods)
    near_support = data["Close"].iloc[-1] <= support_level * 1.05  # within 5% of support level

    # Classify the stock based on RSI and other conditions
    if latest_rsi < 30:
        signal = "BUY (Oversold)"
        # Check for trend reversal signals
        if latest_macd > latest_macd_signal:  # Bullish MACD crossover
            signal += " - MACD Bullish Crossover"
        if data["Close"].iloc[-1] > latest_50_ma and data["Close"].iloc[-1] > latest_200_ma:  # Above both MAs
            signal += " - Above MAs"
        if volume_surge:
            signal += " - Volume Surge"
        if near_support:
            signal += " - Near Support Level"
    elif latest_rsi > 70:
        signal = "SELL (Overbought)"
    else:
        signal = "NEUTRAL (Stable)"

    # Store the result
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

# Convert to DataFrame and print results
pd.set_option("display.max_rows", None)  # Show all rows
rsi_df = pd.DataFrame.from_dict(rsi_signals, orient="index")
print(rsi_df)