# your_project/core/api_manager.py

import requests
import os
import streamlit as st
from typing import Optional, Dict, Any

class APIManager:
    def __init__(self):
        # Use st.secrets if available, or fall back to os.getenv
        self.news_api_key = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY"))
        self.alpha_vantage_api_key = st.secrets.get("ALPHA_VANTAGE_API_KEY", os.getenv("ALPHA_VANTAGE_API_KEY"))
        self.exchange_rate_api_key = st.secrets.get("EXCHANGE_RATE_API_KEY", os.getenv("EXCHANGE_RATE_API_KEY"))

    def fetch_news_articles(self, query: str, limit: int = 10) -> list:
        """
        Fetches news articles related to a query (e.g., ticker symbol) from NewsAPI.
        """
        if not self.news_api_key:
            print("Error: News API key not set. Cannot fetch news.")
            return []

        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}&language=en&sortBy=publishedAt"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('articles', [])[:limit]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for '{query}': {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while fetching news: {e}")
            return []

    def fetch_alpha_vantage_data(self, symbol: str, function: str, outputsize: str = 'compact') -> Dict[str, Any]:
        """
        Fetches financial data from Alpha Vantage.
        """
        if not self.alpha_vantage_api_key:
            print("Error: Alpha Vantage API key not set. Cannot fetch data.")
            return {}

        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize={outputsize}&apikey={self.alpha_vantage_api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Alpha Vantage data for '{symbol}': {e}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while fetching Alpha Vantage data: {e}")
            return {}

    def fetch_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        """
        Fetches the latest exchange rates from the ExchangeRate-API.
        """
        if not self.exchange_rate_api_key:
            print("WARNING: EXCHANGE_RATE_API_KEY not set. Currency conversion disabled.")
            return None

        url = f"https://v6.exchangerate-api.com/v6/{self.exchange_rate_api_key}/latest/{base_currency}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['result'] == 'success':
                return data['conversion_rates']
            else:
                print(f"API Error fetching exchange rates: {data.get('error-type', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching exchange rates: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
