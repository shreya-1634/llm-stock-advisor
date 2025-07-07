from core.api_manager import api_manager
from transformers import pipeline
import streamlit as st

sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_financial_news(ticker):
    news_client = api_manager.get_news_client()
    if not news_client: return []
    
    try:
        news = news_client.get_everything(
            q=ticker,
            language='en',
            page_size=5
        )['articles']
        
        for article in news:
            if article['content']:
                # Sentiment analysis
                sentiment = sentiment_analyzer(article['content'][:512])[0]
                article['sentiment'] = sentiment['label']
                # AI insight
                article['ai_insight'] = generate_ai_insight(article['content'], ticker)
        return news
    except Exception as e:
        st.error(f"News Error: {str(e)}")
        return []

def generate_ai_insight(text, ticker):
    client = api_manager.get_openai()
    if not client: return "AI unavailable"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "system",
                "content": "Analyze this as a financial expert:"
            },{
                "role": "user", 
                "content": f"News about {ticker}: {text[:2000]}"
            }],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return "Analysis failed"
