import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime, timedelta

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        return df["Close"] if not df.empty else None
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def fetch_news_with_links(ticker: str):
    try:
        search_query = f"{ticker} stock news"
        url = f"https://news.google.com/search?q={search_query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, "html.parser")
        articles = soup.select("article h3 a")
        news_html = ""
        for a in articles[:5]:
            title = a.text
            href = a["href"]
            link = f"https://news.google.com{href[1:]}" if href.startswith(".") else href
            news_html += f"- [{title}]({link})\n"
        return news_html
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

def calculate_volatility(prices):
    try:
        if prices is None or prices.empty:
            return None
        returns = prices.pct_change().dropna()
        volatility = returns.std() * 100  # percent
        return volatility
    except Exception as e:
        print(f"Error calculating volatility: {e}")
        return None

def predict_future_prices(prices, days_ahead=7):
    try:
        last_price = prices.iloc[-1]
        volatility = calculate_volatility(prices) / 100
        np.random.seed(42)
        noise = np.random.normal(0, volatility, days_ahead)
        future_prices = [last_price * (1 + n) for n in noise]
        future_dates = pd.date_range(start=prices.index[-1] + pd.Timedelta(days=1), periods=days_ahead)
        return pd.Series(future_prices, index=future_dates)
    except Exception as e:
        print(f"Prediction error: {e}")
        return None
        
def ai_decision_suggestion(news_summary: str, prices: list) -> str:
    if not prices or len(prices) < 2:
        return "❌ Not enough price data for analysis."

    trend = prices[-1] - prices[0]
    news_text = " ".join([item["text"].lower() for item in news_summary if "text" in item])

    if "crash" in news_text or trend < -2:
        return "❌ AI Suggestion: SELL"
    elif "gain" in news_text or trend > 2:
        return "✅ AI Suggestion: BUY"
    else:
        return "➖ AI Suggestion: HOLD"

