# app/utils.py

import yfinance as yf

def fetch_recent_prices(ticker: str, days: int = 60):
    try:
        # Fetch historical data from Yahoo Finance
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)

        # Check if we got any data
        if df.empty or "Close" not in df.columns:
            print("⚠️ Empty DataFrame or missing 'Close' column")
            return None

        # Return last N days of closing prices
        return df["Close"].tail(days)

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None
