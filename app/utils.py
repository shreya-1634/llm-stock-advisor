import yfinance as yf

def fetch_recent_prices(ticker="TCS.NS", days=60):
    df = yf.download(ticker, period="6mo", interval="1d")
    df.dropna(inplace=True)
    return df["Close"].tail(days).values.tolist()
