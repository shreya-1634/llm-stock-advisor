import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from .config import get_logger

logger = get_logger(__name__)

def fetch_stock_data(ticker, period="30d", source="alpha_vantage"):
    try:
        if source == "alpha_vantage":
            return fetch_from_alpha_vantage(ticker, period)
        elif source == "finnhub":
            return fetch_from_finnhub(ticker, period)
        else:
            raise ValueError("Unknown data source")
    except Exception as e:
        logger.error(f"Data fetch failed for {ticker}: {e}")
        return pd.DataFrame()

def fetch_from_alpha_vantage(ticker, period="30d"):
    api_key = st.secrets["api_keys"]["alpha_vantage"]
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={api_key}"

    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError("Invalid response from Alpha Vantage")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
    df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividend", "Split Coef"][:len(df.columns)]
    df = df[["Open", "High", "Low", "Close"]]
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    # Filter by period
    days = int(period.replace("d", "")) if "d" in period else 30
    start_date = datetime.now() - timedelta(days=days)
    df = df[df.index >= start_date]

    return df

def fetch_from_finnhub(ticker, period="30d"):
    api_key = st.secrets["api_keys"]["finnhub"]
    days = int(period.replace("d", "")) if "d" in period else 30
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=days)).timestamp())

    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={api_key}"

    response = requests.get(url)
    data = response.json()

    if data.get("s") != "ok":
        raise ValueError("Invalid response from Finnhub")

    df = pd.DataFrame({
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
    }, index=pd.to_datetime(data["t"], unit="s"))

    df.sort_index(inplace=True)
    return df
