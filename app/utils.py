import yfinance as yf
import requests
import pandas as pd
import streamlit as st

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        return df["Close"]
    except Exception as e:
        print(f"❌ Failed to fetch prices: {e}")
        return None

def fetch_news_with_llm(ticker: str):
    api_key = st.secrets["NEWS_API_KEY"]
    query = ticker.replace(".NS", "").replace(".BO", "").upper()

    url = (
    f"https://newsapi.org/v2/everything?q={query}"
    f"&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        if not articles:
            return f"No recent news found for {ticker}."

        news_summary = ""
        for article in articles:
            title = article["title"]
            source = article["source"]["name"]
            link = article["url"]
            news_summary += f"- [{title}]({link}) ({source})\\n"

        return news_summary.strip()

    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return "❌ Failed to fetch news."

def calculate_volatility(prices: pd.Series, window: int = 5):
    try:
        return prices.pct_change().rolling(window=window).std()
    except:
        return None
