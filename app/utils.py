import yfinance as yf
import requests
import pandas as pd
import streamlit as st
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        return df["Close"]
    except Exception as e:
        print(f"❌ Failed to fetch prices: {e}")
        return None

def fetch_market_volatility(index: str = "^INDIAVIX"):
    try:
        df = yf.download(index, period="7d", interval="1d", auto_adjust=True)
        if not df.empty:
            return round(df["Close"].iloc[-1], 2)
        else:
            return None
    except Exception as e:
        print(f"❌ Failed to fetch VIX: {e}")
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

def predict_future_prices(prices: pd.Series, days_ahead: int = 5):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(prices.values.reshape(-1, 1))

    X, y = [], []
    window_size = 60
    for i in range(window_size, len(scaled)):
        X.append(scaled[i-window_size:i])
        y.append(scaled[i])
    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    last_sequence = scaled[-window_size:]
    predictions = []
    current_input = last_sequence.reshape(1, window_size, 1)

    for _ in range(days_ahead):
        next_price = model.predict(current_input, verbose=0)[0]
        predictions.append(next_price)
        current_input = np.append(current_input[:, 1:, :], [[next_price]], axis=1)

    return scaler.inverse_transform(predictions).flatten()
