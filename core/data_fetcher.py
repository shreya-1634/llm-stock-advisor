import yfinance as yf
from datetime import datetime
from core.config import get_logger

logger = get_logger(__name__)

def fetch_stock_data(ticker, start_date, end_date):
    try:
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            logger.warning(f"No data found for {ticker}")
            raise ValueError(f"No data available for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Data fetch failed: {str(e)}")
        raise

def get_current_price(ticker):
    try:
        logger.debug(f"Getting current price for {ticker}")
        stock = yf.Ticker(ticker)
        price = stock.history(period='1d')['Close'].iloc[-1]
        logger.info(f"Current price for {ticker}: {price}")
        return price
    except Exception as e:
        logger.error(f"Price fetch failed: {str(e)}")
        raise
