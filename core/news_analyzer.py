from core.api_manager import api_manager
import streamlit as st
from transformers import pipeline
import torch  # Add this import

# Initialize sentiment analyzer with error handling
try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
except Exception as e:
    st.error(f"Failed to initialize sentiment analyzer: {str(e)}")
    sentiment_analyzer = None

def fetch_financial_news(ticker):
    if sentiment_analyzer is None:
        st.warning("Sentiment analysis unavailable")
        return []
    
    # Rest of your existing code...
    news_client = api_manager.get_news_client()
    if not news_client: 
        return []
    
    try:
        news = news_client.get_everything(
            q=ticker,
            language='en',
            page_size=5
        )['articles']
        
        for article in news:
            if article['content']:
                try:
                    sentiment = sentiment_analyzer(article['content'][:512])[0]
                    article['sentiment'] = sentiment['label']
                    article['sentiment_score'] = sentiment['score']
                except Exception as e:
                    article['sentiment'] = 'ERROR'
                    article['sentiment_score'] = 0.0
        return news
    except Exception as e:
        st.error(f"News fetch error: {str(e)}")
        return []
