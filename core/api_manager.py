# your_project/core/api_manager.py

import requests
import os
import streamlit as st

class APIManager:
    def __init__(self):
        # Retrieve from st.secrets if available, or fall back to os.getenv
        self.news_api_key = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY"))
        self.alpha_vantage_api_key = st.secrets.get("ALPHA_VANTAGE_API_KEY", os.getenv("ALPHA_VANTAGE_API_KEY"))

    def fetch_news_articles(self, query: str, limit: int = 10) -> list:
        """Fetches news articles using the NewsAPI key."""
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

    def fetch_alpha_vantage_data(self, symbol: str, function: str, outputsize: str = 'compact') -> dict:
        """Fetches financial data from Alpha Vantage."""
        if not self.alpha_vantage_api_key:
            print("Error: Alpha Vantage API key not set.")
            return {}

        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize={outputsize}&apikey={self.alpha_vantage_api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Alpha Vantage data for '{symbol}': {e}")
            return {}
