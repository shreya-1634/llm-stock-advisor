import streamlit as st
from datetime import datetime, timedelta
from transformers import pipeline
import torch
from .api_manager import api_manager
from .config import get_logger

logger = get_logger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = self._init_sentiment_analyzer()
        self.openai_client = api_manager.get_openai()
        logger.info("✅ NewsAnalyzer initialized.")

    def _init_sentiment_analyzer(self):
        try:
            return pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.warning(f"❌ Sentiment analyzer init failed: {e}")
            return None

    def fetch_financial_news(self, ticker, days=7):
        news_client = api_manager.get_news_client()
        if not news_client:
            logger.error("❌ News API client not configured.")
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            logger.info(f"🔍 Fetching news for {ticker} since {from_date}")

            response = news_client.get_everything(
                q=ticker,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=5
            )
            articles = response.get('articles', [])
            logger.info(f"📄 Found {len(articles)} articles")

            enriched = []
            for art in articles:
                enriched.append(self._enrich_article(art, ticker))
            return enriched

        except Exception as e:
            logger.error(f"❌ News fetch failed: {e}")
            return []

    def _enrich_article(self, article, ticker):
        content = article.get("content", "")[:1500]
        sentiment = "neutral"
        score = 0.0

        # Sentiment analysis
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(content[:512])[0]
                sentiment = result["label"].lower()
                score = result["score"]
        except Exception as e:
            logger.warning(f"⚠️ Sentiment analysis failed: {e}")

        # AI insight
        insight = self._get_ai_insight(content, ticker)

        return {
            "title": article.get("title"),
            "source": article.get("source", {}).get("name"),
            "publishedAt": article.get("publishedAt"),
            "description": article.get("description"),
            "url": article.get("url"),
            "sentiment": sentiment.upper(),
            "sentiment_score": score,
            "ai_insight": insight
        }

    def _get_ai_insight(self, content, ticker):
        if not self.openai_client:
            return "AI analysis unavailable"

        try:
            response = self.openai_client.chat.completions.create(
                model=st.secrets.get("GPT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": f"Analyze this news about {ticker}:\n\n{content}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"⚠️ AI insight failed: {e}")
            return "AI insight unavailable"

# Singleton
news_analyzer = NewsAnalyzer()

def display_news_with_insights(news_data):
    if not news_data:
        st.warning("No recent news found.")
        return

    for i, article in enumerate(news_data):
        with st.expander(f"{i+1}. {article.get('title', 'No title')}", expanded=(i == 0)):
            cols = st.columns([1, 4])
            cols[0].metric(
                "Sentiment",
                article['sentiment'].upper(),
                f"{article['sentiment_score']:.0%}"
            )
            cols[1].markdown(f"**Source:** {article.get('source', 'Unknown')}")
            cols[1].markdown(f"**Published:** {article.get('publishedAt', 'N/A')}")

            st.markdown(f"> {article.get('description', 'No description available')}")
            st.markdown(f"**AI Insight:**\n\n{article.get('ai_insight', 'No analysis available')}")

            if article.get("url"):
                st.markdown(f"[🔗 Read Full Article]({article['url']})")

