import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def fetch_all_prices(ticker: str):
    df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
    if df.empty or "Close" not in df.columns:
        print("⚠️ No valid price data found.")
        return None
    return df["Close"]

def calculate_volatility(prices):
    returns = prices.pct_change().dropna()
    return returns.std()

def predict_future_prices(prices, days=5):
    df = prices.reset_index()
    df['Day'] = np.arange(len(df))

    model = LinearRegression()
    model.fit(df[['Day']], df['Close'])

    future_days = np.arange(len(df), len(df) + days)
    future_prices = model.predict(future_days.reshape(-1, 1))
    return future_prices

def fetch_news_with_llm(ticker, api_key):
    try:
        query = f"{ticker} stock news"
        url = f"https://news.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("article h3")
        headlines = [a.get_text() for a in articles[:5]]

        if not headlines:
            return "No major headlines found."

        summary = " | ".join(headlines)
        return summary

    except Exception as e:
        print("❌ News fetch error:", e)
        return "News unavailable."
