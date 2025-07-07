import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock data from Yahoo Finance
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def get_current_price(ticker):
    """
    Get current market price for a ticker
    """
    stock = yf.Ticker(ticker)
    return stock.history(period='1d')['Close'].iloc[-1]

def get_company_info(ticker):
    """
    Get basic company information
    """
    stock = yf.Ticker(ticker)
    return stock.info
