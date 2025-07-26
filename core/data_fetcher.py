# your_project/core/data_fetcher.py

import yfinance as yf
import pandas as pd
import ta # Technical Analysis library
import os

class DataFetcher:
    def __init__(self):
        self.cache_dir = "data/ticker_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_historical_data(self, ticker_symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetches historical stock data using yfinance.
        Caches data locally to reduce API calls.
        'period' can be '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
        """
        cache_path = os.path.join(self.cache_dir, f"{ticker_symbol}_{period}.csv")
        
        # Simple caching logic: load from cache if file exists
        # For a more robust cache, you might check if the cached data is recent enough
        if os.path.exists(cache_path):
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                # Check if data is up-to-date (e.g., if last date in cache is yesterday or today)
                # For simplicity, we just load if exists. Implement more complex logic if needed.
                if not df.empty and df.index[-1].date() == pd.Timestamp.today().date():
                     print(f"Loaded {ticker_symbol} for {period} from fresh cache.")
                     return df
                else:
                    print(f"Cached data for {ticker_symbol} is stale or incomplete, re-fetching.")
                    os.remove(cache_path) # Remove old cache to force re-download
            except Exception as e:
                print(f"Error loading {ticker_symbol} from cache: {e}. Re-fetching data.")
                if os.path.exists(cache_path):
                    os.remove(cache_path) # Remove corrupted cache file

        try:
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period=period)
            
            if not df.empty:
                # Save to cache
                df.to_csv(cache_path)
                print(f"Fetched and cached {ticker_symbol} data for {period}.")
                return df
            else:
                print(f"No data found for {ticker_symbol} using yfinance for period {period}.")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return pd.DataFrame()

    def calculate_rsi(self, df: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculates Relative Strength Index (RSI)."""
        if 'Close' not in df.columns or df['Close'].empty:
            print("Cannot calculate RSI: 'Close' column missing or empty.")
            return pd.Series(dtype='float64')
        return ta.momentum.RSIIndicator(df['Close'], window=window, fillna=True).rsi()

    def calculate_macd(self, df: pd.DataFrame, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9) -> pd.DataFrame:
        """Calculates Moving Average Convergence Divergence (MACD)."""
        if 'Close' not in df.columns or df['Close'].empty:
            print("Cannot calculate MACD: 'Close' column missing or empty.")
            return pd.DataFrame()
        macd_indicator = ta.trend.MACD(df['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=True)
        return pd.DataFrame({
            'MACD': macd_indicator.macd(),
            'MACD_Signal': macd_indicator.macd_signal(),
            'MACD_Diff': macd_indicator.macd_diff() # Histogram
        })

    def calculate_bollinger_bands(self, df: pd.DataFrame, window: int = 20, window_dev: int = 2) -> pd.DataFrame:
        """Calculates Bollinger Bands."""
        if 'Close' not in df.columns or df['Close'].empty:
            print("Cannot calculate Bollinger Bands: 'Close' column missing or empty.")
            return pd.DataFrame()
        bb = ta.volatility.BollingerBands(df['Close'], window=window, window_dev=window_dev, fillna=True)
        return pd.DataFrame({
            'BBL': bb.bollinger_lband(),
            'BBM': bb.bollinger_mavg(),
            'BBU': bb.bollinger_hband()
        })
