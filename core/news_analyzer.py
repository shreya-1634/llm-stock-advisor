import streamlit as st
from datetime import datetime, timedelta
from core.api_manager import api_manager
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = self._init_sentiment_analyzer()

    def _init_sentiment_analyzer(self):
        """Initialize sentiment analyzer with fallback options"""
        try:
            from transformers import pipeline
            import torch
            return pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device="cuda" if torch.cuda.is_available() else "cpu",
                truncation=True
            )
        except ImportError as e:
            logger.warning(f"Transformers not available: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Sentiment analyzer init failed: {str(e)}")
            return None

    def fetch_financial_news(self, ticker, days=7):
        """Fetch and analyze news with multiple fallback mechanisms"""
        if not api_manager.get_news_client():
            st.warning("News API client not configured")
            return []

        try:
            # Fetch news from API
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            news = api_manager.get_news_client().get_everything(
                q=ticker,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=5
            ).get('articles', [])

            # Analyze each article
            analyzed_news = []
            for article in news:
                try:
                    analyzed = self._analyze_article(article, ticker)
                    if analyzed:
                        analyzed_news.append(analyzed)
                except Exception as e:
                    logger.error(f"Article analysis failed: {str(e)}")
                    continue
            
            return analyzed_news

        except Exception as e:
            logger.error(f"News fetch failed: {str(e)}")
            st.error("Failed to fetch news. Please try again later.")
            return []

    def _analyze_article(self, article, ticker):
        """Analyze individual article with sentiment and AI insights"""
        if not article.get('content'):
            return None

        content = article['content'][:2000]  # Truncate to prevent token limits
        
        # Basic sentiment analysis
        article['sentiment'] = 'neutral'
        article['sentiment_score'] = 0.0
        if self.sentiment_analyzer:
            try:
                sentiment = self.sentiment_analyzer(content)[0]
                article['sentiment'] = sentiment['label'].lower()
                article['sentiment_score'] = sentiment['score']
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {str(e)}")

        # AI insights (with fallback)
        article['ai_insight'] = self._get_ai_insight(content, ticker)
        
        return article

    def _get_ai_insight(self, text, ticker):
        """Get AI-generated insight with proper error handling"""
        try:
            client = api_manager.get_openai()
            if not client:
                return "AI analysis unavailable"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # More cost-effective than GPT-4
                messages=[{
                    "role": "system",
                    "content": f"You are a financial analyst specializing in {ticker}. Provide concise insights."
                }, {
                    "role": "user",
                    "content": f"Analyze this news text about {ticker}:\n\n{text[:1500]}\n\nProvide:\n1. Key sentiment\n2. Potential market impact\n3. Investor considerations"
                }],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI insight failed: {str(e)}")
            return "Analysis unavailable"

def display_news_with_insights(news):
    """Display news cards with consistent formatting"""
    if not news:
        st.warning("No recent news found")
        return

    for i, article in enumerate(news):
        with st.expander(f"{i+1}. {article.get('title', 'No title')}", expanded=i==0):
            cols = st.columns([1, 4])
            cols[0].metric(
                "Sentiment", 
                article['sentiment'].upper(),
                f"{article['sentiment_score']:.0%}",
                delta_color="off"
            )
            
            cols[1].write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
            cols[1].write(f"**Published:** {article.get('publishedAt', 'Date unavailable')}")
            
            st.write(article.get('description', 'No description available'))
            st.divider()
            
            st.write("**AI Insight:**")
            st.write(article.get('ai_insight', 'No analysis available'))
            
            if article.get('url'):
                st.markdown(f"[Read full article ↗]({article['url']})", unsafe_allow_html=True)

# Singleton instance
news_analyzer = NewsAnalyzer()
