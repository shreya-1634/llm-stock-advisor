import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        if df.empty or "Close" not in df.columns:
            return None
        return df["Close"]
    except Exception as e:
        print("⚠️ Error fetching stock data:", e)
        return None

def fetch_news_with_links(ticker):
    try:
        query = f"{ticker} stock"
        url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.select("article h3")

        news = []
        for a in articles[:5]:
            title = a.get_text()
            link_tag = a.find("a")
            if link_tag and link_tag['href']:
                url = "https://news.google.com" + link_tag['href'][1:]
                news.append((title, url))
        return news
    except Exception as e:
        print("❌ News fetch failed:", e)
        return []

def calculate_volatility(prices: pd.Series):
    returns = prices.pct_change().dropna()
    return returns.std() * 100

def predict_future_prices(prices: pd.Series, days_ahead=7):
    try:
        df = prices.reset_index()
        df['timestamp'] = df['Date'].map(datetime.toordinal)
        X = np.array(df['timestamp']).reshape(-1, 1)
        y = np.array(df['Close'])

        model = LinearRegression()
        model.fit(X, y)

        last_day = df['timestamp'].iloc[-1]
        future_days = np.array([last_day + i for i in range(1, days_ahead + 1)])
        future_preds = model.predict(future_days.reshape(-1, 1))
        future_dates = [datetime.fromordinal(int(d)) for d in future_days]

        return pd.Series(future_preds, index=future_dates)
    except Exception as e:
        print("❌ Prediction error:", e)
        return None
