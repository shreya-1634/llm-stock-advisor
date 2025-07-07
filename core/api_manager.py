import streamlit as st
import json
from openai import OpenAI  # Updated import
from newsapi import NewsApiClient

class APIManager:
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        with open("static/config.json") as f:
            self.config = json.load(f)
    
    def get_news_client(self):
        try:
            return NewsApiClient(api_key=st.secrets["NEWS_API_KEY"])
        except Exception as e:
            st.error(f"NewsAPI Error: {str(e)}")
            return None

    def get_openai(self):
        try:
            return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # New client initialization
        except Exception as e:
            st.error(f"OpenAI Error: {str(e)}")
            return None

api_manager = APIManager()
