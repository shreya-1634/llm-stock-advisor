import pandas as pd
import requests
import os
from core.config import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

def fetch_stock_data(ticker, period="30d", source="alpha_vantage"):
    logger.info(f"Fetching {period} data for {ticker} using {source}")

    if source == "alpha_vantage":
        return fetch_from_alpha_vantage(ticker, period)
    elif source == "finnhub":
        return fetch_from_finnhub(ticker, period)
    else:
        logger.error(f"Unknown source: {source}")
        return pd.DataFrame()

def fetch_from_alpha_vantage(ticker, period):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={api_key}&outputsize=full"
    r = requests.get(url)

    if r.status_code != 200 or "Time Series" not in r.text:
        return pd.DataFrame()

    try:
        data = r.json()["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(data, orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividends", "Split Coefficient"]
        df.sort_index(inplace=True)

        days = int(period.replace("d", ""))
        start = datetime.now() - timedelta(days=days)
        return df[df.index >= start]
    except Exception as e:
        logger.error(f"Alpha Vantage Error: {e}")
        return pd.DataFrame()

def fetch_from_finnhub(ticker, period):
    api_key = os.getenv("FINNHUB_API_KEY")
    days = int(period.replace("d", ""))
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=days)).timestamp())
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={api_key}"
    r = requests.get(url)

    try:
        data = r.json()
        if data.get("s") != "ok":
            return pd.DataFrame()

        df = pd.DataFrame({
            "Open": data["o"],
            "High": data["h"],
            "Low": data["l"],
            "Close": data["c"],
            "Volume": data["v"]
        }, index=pd.to_datetime(data["t"], unit="s"))
        return df
    except Exception as e:
        logger.error(f"Finnhub Error: {e}")
        return pd.DataFrame()
