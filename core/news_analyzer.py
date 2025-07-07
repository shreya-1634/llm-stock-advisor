import requests
from transformers import pipeline
from datetime import datetime, timedelta
import streamlit as st

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news(ticker, days=7):
    """
    Fetch news articles related to the stock ticker
    """
    NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # Replace with your actual key
    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    url = f"https://newsapi.org/v2/everything?q={ticker}&from={from_date}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        # Analyze sentiment for each article
        for article in articles:
            if article['content']:
                sentiment = sentiment_analyzer(article['content'][:512])[0]
                article['sentiment'] = sentiment['label']
                article['sentiment_score'] = sentiment['score']
        return articles
    else:
        st.error("Failed to fetch news")
        return []

def display_news(articles):
    """
    Display news articles with sentiment analysis in Streamlit
    """
    if not articles:
        st.warning("No recent news found for this stock")
        return
    
    for article in articles[:5]:  # Show top 5 articles
        with st.expander(f"{article['title']} ({article['sentiment']} - {article['sentiment_score']:.2f})"):
            st.write(f"**Source:** {article['source']['name']}")
            st.write(f"**Published At:** {article['publishedAt']}")
            st.write(article['description'])
            if article['url']:
                st.markdown(f"[Read more]({article['url']})", unsafe_allow_html=True)
