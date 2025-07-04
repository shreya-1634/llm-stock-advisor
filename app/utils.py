import yfinance as yf
import requests
import pandas as pd
import numpy as np

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        if df.empty or "Close" not in df.columns:
            print("⚠️ Empty DataFrame or missing 'Close' column")
            return None
        return df
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def fetch_news_with_llm(ticker: str):
    try:
        query = f"{ticker} stock news site:finance.yahoo.com"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url)
        response.encoding = "utf-8"

        if response.status_code != 200:
            return None

        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        headlines = [item.find("title").text for item in items[:5]]
        return "\n".join([f"- {headline}" for headline in headlines])
    except Exception as e:
        print(f"❌ News Fetch Error: {e}")
        return None

def calculate_volatility(df: pd.DataFrame):
    returns = df["Close"].pct_change().dropna()
    volatility = np.std(returns) * np.sqrt(252)  # annualized volatility
    return volatility

def predict_future_prices(df, days_ahead=7):
    from sklearn.linear_model import LinearRegression
    import numpy as np

    df = df.reset_index()
    df["timestamp"] = df["Date"].map(pd.Timestamp.timestamp)

    X = df["timestamp"].values.reshape(-1, 1)
    y = df["Close"].values

    model = LinearRegression().fit(X, y)

    last_timestamp = df["timestamp"].iloc[-1]
    future_timestamps = np.array([last_timestamp + i * 86400 for i in range(1, days_ahead + 1)])
    future_prices = model.predict(future_timestamps.reshape(-1, 1))

    # ✅ FIXED HERE
    future_dates = pd.date_range(start=df["Date"].iloc[-1] + pd.Timedelta(days=1), periods=days_ahead)

    return pd.Series(future_prices.flatten(), index=future_dates)
