from datetime import datetime, timedelta
from core.api_manager import api_manager
import streamlit as st
import traceback
from core.config import get_logger

logger = get_logger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = self._init_sentiment_analyzer()
        logger.info("NewsAnalyzer initialized")

    def _init_sentiment_analyzer(self):
        try:
            from transformers import pipeline
            import torch
            logger.info("Initializing sentiment analyzer")
            return pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
        except Exception as e:
            logger.error(f"Sentiment analyzer init failed: {str(e)}\n{traceback.format_exc()}")
            return None

    def fetch_financial_news(self, ticker, days=7):
        try:
            logger.info(f"Fetching news for {ticker} (last {days} days)")
            news_client = api_manager.get_news_client()
            
            if not news_client:
                logger.error("News API client not available")
                return []
                
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            response = news_client.get_everything(
                q=ticker,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=5
            )
            
            articles = response.get('articles', [])
            logger.debug(f"Found {len(articles)} articles for {ticker}")
            
            analyzed_articles = []
            for article in articles:
                try:
                    analyzed = self._analyze_article(article, ticker)
                    if analyzed:
                        analyzed_articles.append(analyzed)
                except Exception as e:
                    logger.warning(f"Article analysis failed: {str(e)}\nTitle: {article.get('title')}")
                    continue
                    
            logger.info(f"Returning {len(analyzed_articles)} analyzed articles")
            return analyzed_articles
            
        except Exception as e:
            logger.error(f"News fetch failed: {str(e)}\n{traceback.format_exc()}")
            return []

    def _analyze_article(self, article, ticker):
        content = article.get('content', '')[:2000]
        
        # Sentiment analysis
        article['sentiment'] = 'neutral'
        article['sentiment_score'] = 0.0
        if self.sentiment_analyzer and content:
            try:
                result = self.sentiment_analyzer(content)[0]
                article['sentiment'] = result['label'].lower()
                article['sentiment_score'] = result['score']
                logger.debug(f"Analyzed sentiment: {article['sentiment']} ({article['sentiment_score']:.2f})")
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {str(e)}")
        
        # AI insight
        article['ai_insight'] = self._get_ai_insight(content, ticker)
        return article

    def _get_ai_insight(self, text, ticker):
        try:
            client = api_manager.get_openai()
            if not client:
                logger.warning("OpenAI client not available")
                return "AI analysis unavailable"
                
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": f"Analyze this news about {ticker} as a financial expert:"
                }, {
                    "role": "user", 
                    "content": text[:1500]
                }],
                max_tokens=200,
                temperature=0.3
            )
            insight = response.choices[0].message.content
            logger.debug(f"Generated AI insight: {insight[:50]}...")
            return insight
        except Exception as e:
            logger.error(f"AI insight failed: {str(e)}\n{traceback.format_exc()}")
            return "Analysis failed"

news_analyzer = NewsAnalyzer()

def display_news_with_insights(news):
    if not news:
        logger.warning("No news to display")
        st.warning("No recent news found")
        return
        
    logger.debug(f"Displaying {len(news)} news items")
    for i, article in enumerate(news):
        with st.expander(f"{i+1}. {article.get('title', 'No title')}", expanded=i==0):
            # Display logic...
