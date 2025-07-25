# core/api_manager.py
import openai
from newsapi import NewsApiClient
import logging
import streamlit as st

class APIManager:
    def __init__(self):
        self.news_api_key = None
        self.openai_key = None
        self.news_client = None
        self.openai_client = None
        self.load_api_keys()

    def load_api_keys(self):
        try:
            self.news_api_key = st.secrets["news_api"]["api_key"]
            self.news_client = NewsApiClient(api_key=self.news_api_key)
        except Exception as e:
            logging.warning("❗️NewsAPI key missing or misconfigured in secrets.")

        try:
            self.openai_key = st.secrets["openai"]["api_key"]
            openai.api_key = self.openai_key
            self.openai_client = openai
        except Exception as e:
            logging.warning("❗️OpenAI API key missing or misconfigured in secrets.")

    def get_news_client(self):
        return self.news_client

    def get_openai(self):
        return self.openai_client


# Global instance
api_manager = APIManager()
