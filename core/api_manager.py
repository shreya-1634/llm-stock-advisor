import streamlit as st
import json
import openai
from newsapi import NewsApiClient

class APIManager:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        with open("static/config.json") as f:
            return json.load(f)
    
    def get_news_client(self):
        try:
            api_key = st.secrets.get("NEWS_API_KEY", self.config["API_KEYS"]["NEWS_API"])
            return NewsApiClient(api_key=api_key)
        except Exception as e:
            st.error(f"NewsAPI Error: {str(e)}")
            return None

    def get_openai(self):
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", self.config["API_KEYS"]["OPENAI_API"])
            openai.api_key = api_key
            return openai
        except Exception as e:
            st.error(f"OpenAI Error: {str(e)}")
            return None

api_manager = APIManager()
