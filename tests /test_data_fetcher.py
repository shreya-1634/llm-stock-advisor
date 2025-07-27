# your_project/tests/test_data_fetcher.py

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import os
import ta # Technical Analysis library

# Adjust imports based on your exact project structure
from core.data_fetcher import DataFetcher

# --- Fixtures ---

@pytest.fixture
def mock_yfinance_history():
    """Mocks yfinance.Ticker().history() to return a predictable DataFrame."""
    # Create a dummy DataFrame that resembles yfinance output
    data = {
        'Open': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115, 114, 116, 118, 117, 119, 120],
        'High': [103, 104, 103, 105, 107, 106, 108, 110, 109, 111, 112, 114, 113, 115, 117, 116, 118, 120, 119, 121, 122],
        'Low': [99, 101, 100, 102, 104, 103, 105, 107, 106, 108, 109, 111, 110, 112, 114, 113, 115, 117, 116, 118, 119],
        'Close': [102, 101, 103, 104, 106, 105, 107, 109, 108, 110, 111, 113, 112, 114, 116, 115, 117, 119, 118, 120, 121],
        'Volume': [100000, 110000, 90000, 120000, 105000, 115000, 95000, 125000, 100000, 130000, 100000, 110000, 90000, 120000, 105000, 115000, 95000, 125000, 100000, 130000, 100000]
    }
    # Create a date range as index, ensure enough data for indicators like RSI (14 days)
    dates = pd.date_range(start='2023-01-01', periods=len(data['Close']))
    df = pd.DataFrame(data, index=dates)
    return df

@pytest.fixture
def data_fetcher_instance():
    """Provides a DataFetcher instance, ensuring a clean cache directory."""
    test_cache_dir = "tests/test_cache"
    # Ensure a clean cache directory for each test
    if os.path.exists(test_cache_dir):
        import shutil
        shutil.rmtree(test_cache_dir)
    os.makedirs(test_cache_dir)

    # Patch the cache_dir to point to our test directory
    with patch('core.data_fetcher.DataFetcher.cache_dir', test_cache_dir):
        yield DataFetcher()
    
    # Clean up after test
    if os.path.exists(test_cache_dir):
        import shutil
        shutil.rmtree(test_cache_dir)


# --- Test Cases ---

def test_fetch_historical_data_fresh(data_fetcher_instance, mock_yfinance_history):
    """Test fetching fresh historical data and caching."""
    ticker = "TEST"
    period = "1mo"
    cache_path = os.path.join(data_fetcher_instance.cache_dir, f"{ticker}_{period}.csv")

    # Mock yfinance.Ticker and its history method
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = mock_yfinance_history.copy() # Return a copy to avoid modification

        df = data_fetcher_instance.fetch_historical_data(ticker, period)

        mock_ticker.assert_called_once_with(ticker)
        mock_ticker_instance.history.assert_called_once_with(period=period)
        assert not df.empty
        assert os.path.exists(cache_path) # Check if file was cached
        pd.testing.assert_frame_equal(df, mock_yfinance_history) # Check content

def test_fetch_historical_data_from_cache(data_fetcher_instance, mock_yfinance_history):
    """Test fetching historical data from cache."""
    ticker = "TEST2"
    period = "1mo"
    cache_path = os.path.join(data_fetcher_instance.cache_dir, f"{ticker}_{period}.csv")

    # Manually create a cached file
    mock_yfinance_history.to_csv(cache_path)

    # Mock yfinance.Ticker to ensure it's NOT called
    with patch('yfinance.Ticker') as mock_ticker:
        df = data_fetcher_instance.fetch_historical_data(ticker, period)

        mock_ticker.assert_not_called() # Crucial: should not call yfinance if cached
        assert not df.empty
        pd.testing.assert_frame_equal(df, mock_yfinance_history)

def test_calculate_rsi(data_fetcher_instance, mock_yfinance_history):
    """Test RSI calculation."""
    # Ensure we have enough data for RSI calculation (default window is 14)
    if len(mock_yfinance_history) < 14:
        pytest.skip("Not enough data in mock_yfinance_history for RSI calculation.")
    
    rsi_series = data_fetcher_instance.calculate_rsi(mock_yfinance_history)
    
    assert not rsi_series.empty
    assert rsi_series.name == 'rsi' # Check default name from TA library
    assert rsi_series.iloc[-1] > 0 # RSI should be positive
    assert rsi_series.iloc[-1] < 100 # RSI should be less than 100
    # You can also compare a known RSI value for a specific dataset if you pre-calculate it

def test_calculate_macd(data_fetcher_instance, mock_yfinance_history):
    """Test MACD calculation."""
    if len(mock_yfinance_history) < 26: # MACD needs at least 26 periods
        pytest.skip("Not enough data in mock_yfinance_history for MACD calculation.")

    macd_df = data_fetcher_instance.calculate_macd(mock_yfinance_history)
    
    assert not macd_df.empty
    assert 'MACD' in macd_df.columns
    assert 'MACD_Signal' in macd_df.columns
    assert 'MACD_Diff' in macd_df.columns
    # Add assertions for typical MACD values if you have a known expected output
    assert macd_df['MACD'].iloc[-1] is not None
    assert macd_df['MACD_Signal'].iloc[-1] is not None
    assert macd_df['MACD_Diff'].iloc[-1] is not None

def test_calculate_rsi_empty_df(data_fetcher_instance):
    """Test RSI calculation with an empty DataFrame."""
    empty_df = pd.DataFrame()
    rsi_series = data_fetcher_instance.calculate_rsi(empty_df)
    assert rsi_series.empty
    assert rsi_series.dtype == 'float64' # Ensure correct type even if empty

def test_calculate_macd_no_close_column(data_fetcher_instance, mock_yfinance_history):
    """Test MACD calculation with DataFrame missing 'Close' column."""
    df_no_close = mock_yfinance_history.drop(columns=['Close'])
    macd_df = data_fetcher_instance.calculate_macd(df_no_close)
    assert macd_df.empty
