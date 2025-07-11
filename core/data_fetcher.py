import requests
import pandas as pd
import streamlit as st
from core.config import get_logger

logger = get_logger(__name__)

def fetch_stock_data(ticker, source="alpha_vantage"):
    try:
        if source == "alpha_vantage":
            return fetch_from_alpha_vantage(ticker)
        elif source == "finnhub":
            return fetch_from_finnhub(ticker)
        else:
            raise ValueError("Unknown data source")
    except Exception as e:
        logger.error(f"Data fetch failed for {ticker}: {e}")
        return pd.DataFrame()

def fetch_from_alpha_vantage(ticker):
    api_key = st.secrets["api_keys"]["alpha_vantage"]
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=compact&apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError("Invalid response from Alpha Vantage")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index', dtype=float)
    df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividend", "Split Coef"][:len(df.columns)]
    df = df[["Open", "High", "Low", "Close"]]
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def fetch_from_finnhub(ticker):
    api_key = st.secrets["api_keys"]["finnhub"]
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&count=100&token={api_key}"
    
    response = requests.get(url)
    data = response.json()

    if data.get("s") != "ok":
        raise ValueError("Invalid response from Finnhub")

    df = pd.DataFrame({
        "Date": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"]
    })
    df.set_index("Date", inplace=True)
    return df

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period='1d')['Close'].iloc[-1]
        logger.info(f"Current price of {ticker}: {price}")
        return price
    except Exception as e:
        logger.error(f"Error fetching current price: {str(e)}")
        return None
