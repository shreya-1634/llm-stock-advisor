import yfinance as yf
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
from datetime import timedelta


def fetch_all_prices(ticker: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        if df.empty or "Close" not in df.columns:
            print("⚠️ Empty DataFrame or missing 'Close' column")
            return pd.DataFrame()
        return df[["Close"]].rename(columns={"Close": "Price"})
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()


def fetch_news_with_links(ticker: str):
    try:
        query = f"{ticker} stock news"
        url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("article h3 a")
        news = []

        for article in articles[:5]:
            headline = article.text.strip()
            link = "https://news.google.com" + article.get("href")[1:]  # remove dot at start
            news.append((headline, link))

        return news
    except Exception as e:
        print(f"❌ Failed to fetch news: {e}")
        return []


def calculate_volatility(df: pd.DataFrame, days: int = 30) -> float:
    try:
        recent = df["Price"].tail(days)
        returns = recent.pct_change().dropna()
        volatility = np.std(returns) * np.sqrt(252)  # annualized volatility
        return round(volatility * 100, 2)  # in percentage
    except Exception as e:
        print(f"❌ Error calculating volatility: {e}")
        return 0.0


def predict_future_prices(df: pd.DataFrame, days_ahead: int = 7) -> pd.Series:
    try:
        df = df.reset_index()
        df["Date_Ordinal"] = pd.to_datetime(df["Date"]).map(pd.Timestamp.toordinal)

        X = df[["Date_Ordinal"]]
        y = df["Price"]

        model = LinearRegression()
        model.fit(X, y)

        last_date = df["Date"].iloc[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        future_ordinals = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)
        future_prices = model.predict(future_ordinals)

        return pd.Series(future_prices, index=future_dates)
    except Exception as e:
        print(f"❌ Error predicting future prices: {e}")
        return pd.Series()
