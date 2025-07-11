import openai
import os
from newsapi import NewsApiClient
from .config import get_logger

logger = get_logger(__name__)

class APIManager:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", None)
        self.newsapi_key = os.getenv("NEWS_API_KEY", None)

        self._openai_client = None
        self._news_client = None

        if self.openai_api_key:
            try:
                openai.api_key = self.openai_api_key
                self._openai_client = openai
                logger.info("✅ OpenAI client initialized.")
            except Exception as e:
                logger.error(f"❌ OpenAI init failed: {e}")

        if self.newsapi_key:
            try:
                self._news_client = NewsApiClient(api_key=self.newsapi_key)
                logger.info("✅ NewsAPI client initialized.")
            except Exception as e:
                logger.error(f"❌ NewsAPI init failed: {e}")

    def get_openai(self):
        if not self._openai_client:
            logger.warning("⚠️ OpenAI client not available.")
        return self._openai_client

    def get_news_client(self):
        if not self._news_client:
            logger.warning("⚠️ News API client not available.")
        return self._news_client

# Singleton
api_manager = APIManager()
