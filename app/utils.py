import yfinance as yf

def fetch_recent_prices(ticker="TCS.NS", days=60):
    df = yf.download(ticker, period="6mo", interval="1d")
    df.dropna(inplace=True)
    return df["Close"].tail(days).values.tolist()
import yfinance as yf

def fetch_recent_prices(ticker: str, days: int = 60):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        if df.empty or "Close" not in df.columns:
            return None
        return df["Close"].tail(days).tolist()
    except Exception as e:
        print(f"❌ Error fetching stock data: {e}")
        return None
