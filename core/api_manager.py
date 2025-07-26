# your_project/core/api_manager.py

import os
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

class APIManager:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        # self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY") # If you use Alpha Vantage directly

    def fetch_news_articles(self, query: str, limit: int = 10) -> list:
        """
        Fetches news articles related to a query (e.g., ticker symbol) from NewsAPI.
        NewsAPI: https://newsapi.org/
        """
        if not self.news_api_key:
            print("Error: News API key not set in .env. Cannot fetch news.")
            return []

        # NewsAPI endpoint for general search (everything)
        # You can also use /v2/top-headlines for more curated news
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}&language=en&sortBy=publishedAt"
        
        try:
            response = requests.get(url, timeout=10) # Add timeout to prevent hanging
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()
            return data.get('articles', [])[:limit]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for '{query}': {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while fetching news: {e}")
            return []

    # Example of how you might add another API (e.g., if you choose Alpha Vantage for some data)
    # def fetch_alpha_vantage_data(self, symbol: str, function: str, interval: str = '5min') -> dict:
    #     if not self.alpha_vantage_api_key:
    #         print("Alpha Vantage API key not set in .env.")
    #         return {}
    #     
    #     url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={self.alpha_vantage_api_key}"
    #     try:
    #         response = requests.get(url, timeout=10)
    #         response.raise_for_status()
    #         return response.json()
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error fetching Alpha Vantage data: {e}")
    #         return {}
