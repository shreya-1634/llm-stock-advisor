import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError(f"No data found for {ticker}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch data: {str(e)}")

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period='1d')['Close'].iloc[-1]
    except Exception as e:
        raise Exception(f"Failed to get current price: {str(e)}")

def get_company_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        raise Exception(f"Failed to get company info: {str(e)}")
