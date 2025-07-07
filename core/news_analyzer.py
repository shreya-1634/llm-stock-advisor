from core.api_manager import api_manager
from transformers import pipeline
import streamlit as st
from datetime import datetime, timedelta

sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_financial_news(ticker):
    news_client = api_manager.get_news_client()
    if not news_client:
        return []
    
    try:
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        news = news_client.get_everything(
            q=ticker,
            from_param=from_date,
            language='en',
            sort_by='relevancy',
            page_size=5
        )['articles']
        
        for article in news:
            if article['content']:
                sentiment = sentiment_analyzer(article['content'][:512])[0]
                article['sentiment'] = sentiment['label']
                article['sentiment_score'] = sentiment['score']
                article['ai_insight'] = generate_ai_insight(article['content'], ticker)
        return news
    except Exception as e:
        st.error(f"News fetch error: {str(e)}")
        return []

def generate_ai_insight(text, ticker):
    openai = api_manager.get_openai()
    if not openai:
        return "AI analysis unavailable"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "system",
                "content": "You are a financial analyst. Provide concise insights about this news article."
            }, {
                "role": "user",
                "content": f"Analyze this news about {ticker}:\n\n{text[:2000]}"
            }],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT analysis failed: {str(e)}")
        return "Analysis error"

def display_news_with_insights(news):
    if not news:
        st.warning("No recent news found")
        return
    
    for article in news:
        with st.expander(f"{article['title']} ({article['sentiment']} - {article['sentiment_score']:.2f})"):
            st.write(f"**Source:** {article['source']['name']}")
            st.write(f"**Published:** {article['publishedAt']}")
            st.write(article['description'])
            
            st.markdown("---")
            st.write("**AI Insight:**")
            st.write(article.get('ai_insight', 'No analysis available'))
            
            if article['url']:
                st.markdown(f"[Read full article]({article['url']})", unsafe_allow_html=True)
