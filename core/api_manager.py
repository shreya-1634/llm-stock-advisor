import streamlit as st
import json
from openai import OpenAI
from newsapi import NewsApiClient
from core.config import get_logger

logger = get_logger(__name__)

class APIManager:
    def __init__(self):
        self._load_config()
        logger.info("API Manager initialized")
    
    def _load_config(self):
        try:
            with open("static/config.json") as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Config load failed: {str(e)}")
            self.config = {}

    def get_news_client(self):
        try:
            api_key = st.secrets.get("NEWS_API_KEY", self.config["API_KEYS"]["NEWS_API"])
            return NewsApiClient(api_key=api_key)
        except Exception as e:
            logger.error(f"NewsAPI Error: {str(e)}")
            return None

    def get_openai(self):
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", self.config["API_KEYS"]["OPENAI_API"])
            return OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"OpenAI Error: {str(e)}")
            return None

api_manager = APIManager()
