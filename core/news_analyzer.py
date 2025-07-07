from core.api_manager import api_manager
from transformers import pipeline
import streamlit as st

sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news(ticker):
    news_client = api_manager.get_news_client()
    if not news_client: return []
    
    try:
        return news_client.get_everything(
            q=ticker,
            language='en',
            sort_by='relevancy',
            page_size=5
        )['articles']
    except Exception as e:
        st.error(f"News fetch failed: {str(e)}")
        return []

def analyze_with_gpt(text, ticker):
    openai = api_manager.get_openai()
    if not openai: return "GPT analysis unavailable"
    
    try:
        response = openai.ChatCompletion.create(
            model=st.secrets.get("GPT_MODEL", "gpt-4-turbo-preview"),
            messages=[{
                "role": "user",
                "content": f"Analyze this news about {ticker} as a financial expert:\n{text[:2000]}"
            }],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT analysis failed: {str(e)}")
        return "Analysis error"
