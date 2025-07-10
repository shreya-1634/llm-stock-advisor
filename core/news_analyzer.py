import streamlit as st
from datetime import datetime, timedelta
from .api_manager import api_manager
from transformers import pipeline
import torch
from .config import get_logger

logger = get_logger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = self._init_sentiment_analyzer()
        logger.info("News Analyzer initialized")

    def _init_sentiment_analyzer(self):
        try:
            return pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
        except Exception as e:
            logger.warning(f"Sentiment analyzer init failed: {str(e)}")
            return None

    def fetch_financial_news(self, ticker, days=7):
        news_client = api_manager.get_news_client()
        if not news_client:
            logger.error("News API client not configured")
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            logger.info(f"Fetching news for {ticker} since {from_date}")
            
            response = news_client.get_everything(
                q=ticker,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=5
            )
            articles = response.get('articles', [])
            logger.debug(f"Found {len(articles)} articles")

            analyzed_articles = []
            for article in articles:
                try:
                    analyzed = self._analyze_article(article, ticker)
                    if analyzed:
                        analyzed_articles.append(analyzed)
                except Exception as e:
                    logger.warning(f"Article analysis failed: {str(e)}")
            
            return analyzed_articles

        except Exception as e:
            logger.error(f"News fetch failed: {str(e)}")
            return []

    def _analyze_article(self, article, ticker):
        if not article.get('content'):
            return None

        content = article['content'][:2000]  # Truncate to prevent token limits
        
        # Sentiment analysis
        article['sentiment'] = 'neutral'
        article['sentiment_score'] = 0.0
        if self.sentiment_analyzer:
            try:
                result = self.sentiment_analyzer(content[:512])[0]
                article['sentiment'] = result['label'].lower()
                article['sentiment_score'] = result['score']
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {str(e)}")

        # AI insight
        article['ai_insight'] = self._get_ai_insight(content, ticker)
        return article

    def _get_ai_insight(self, text, ticker):
        client = api_manager.get_openai()
        if not client:
            return "AI analysis unavailable"

        try:
            response = client.chat.completions.create(
                model=st.secrets.get("GPT_MODEL", "gpt-3.5-turbo"),
                messages=[{
                    "role": "system",
                    "content": "You are a financial analyst. Provide concise insights about this news."
                }, {
                    "role": "user",
                    "content": f"Analyze this news about {ticker}:\n\n{text[:1500]}"
                }],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI insight failed: {str(e)}")
            return "Analysis unavailable"

def display_news_with_insights(news):
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
