# core/data_fetcher.py
import yfinance as yf
import pandas as pd
import logging

def fetch_stock_data(ticker, start="2020-01-01", end=None):
    try:
        df = yf.download(ticker, start=start, end=end)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()
