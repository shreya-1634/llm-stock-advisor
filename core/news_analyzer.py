import streamlit as st
from newsapi import NewsApiClient
import requests
from transformers import pipeline
import torch
from datetime import datetime, timedelta
from .config import get_logger
from .api_manager import api_manager

logger = get_logger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.newsapi = api_manager.get_news_client()
        self.sentiment = self._init_sentiment_analyzer()
        self.openai = api_manager.get_openai()
        logger.info("NewsAnalyzer initialized.")

    def _init_sentiment_analyzer(self):
        try:
            return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english",
                            device=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            logger.warning(f"Sentiment pipeline init failed: {e}")
            return None

    def fetch_news(self, ticker, days=7, max_articles=5):
        if not self.newsapi:
            logger.error("News API client not configured.")
            return []

        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            articles = self.newsapi.get_everything(
                q=ticker,
                from_param=from_date,
                language="en",
                sort_by="relevancy",
                page_size=max_articles
            ).get("articles", [])
            logger.info(f"Fetched {len(articles)} news for {ticker} since {from_date}")
            enriched = [self._process_article(a, ticker) for a in articles if a.get("content")]
            return enriched
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return []

    def _process_article(self, art, ticker):
        content = art["content"][:1500]
        sentiment = "NEUTRAL"
        score = 0.0
        if self.sentiment:
            try:
                res = self.sentiment(content[:512])[0]
                sentiment = res["label"]
                score = res["score"]
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        insight = self._get_ai_insight(content, ticker)
        return {
            "title": art.get("title"),
            "source": art.get("source", {}).get("name"),
            "publishedAt": art.get("publishedAt"),
            "description": art.get("description"),
            "url": art.get("url"),
            "sentiment": sentiment,
            "sentiment_score": score,
            "ai_insight": insight
        }

    def _get_ai_insight(self, content, ticker):
        if not self.openai:
            return "AI analysis unavailable"
        try:
            resp = self.openai.chat.completions.create(
                model=st.secrets.get("GPT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": f"Summarize: {content}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI insight error: {e}")
            return "AI insight unavailable"

    def display(self, articles):
        if not articles:
            st.warning("No recent news found for this ticker.")
        for i, art in enumerate(articles):
            with st.expander(f"{i+1}. {art['title']}", expanded=(i==0)):
                cols = st.columns([1, 4])
                cols[0].metric(
                    "Sentiment", art["sentiment"], f"{art['sentiment_score']:.0%}"
                )
                cols[1].markdown(f"**Source:** {art['source']}  \n**Published:** {art['publishedAt']}")
                st.write(art.get("description", "No description"))
                st.write("**AI Insight:**"); st.write(art["ai_insight"])
                st.markdown(f"[Read full article ↗]({art['url']})")

news_analyzer = NewsAnalyzer()
