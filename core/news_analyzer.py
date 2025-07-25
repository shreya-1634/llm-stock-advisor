import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from transformers import pipeline
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("492fa1e881394250b2eb012b0f162459")  # Get it from https://newsapi.org/
sentiment_pipeline = pipeline("sentiment-analysis")

def fetch_news(ticker: str, max_articles: int = 10):
    """
    Fetches recent news articles for a ticker using NewsAPI.
    If NewsAPI fails or rate limited, it tries Yahoo Finance RSS.
    Returns list of (headline, url) tuples.
    """
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&pageSize={max_articles}"
        response = requests.get(url)
        data = response.json()
        
        if "articles" in data:
            news = [(article["title"], article["url"]) for article in data["articles"]]
            return news
        else:
            return fetch_news_from_yahoo(ticker, max_articles)

    except Exception as e:
        print(f"NewsAPI failed: {e}")
        return fetch_news_from_yahoo(ticker, max_articles)


def fetch_news_from_yahoo(ticker: str, max_articles: int = 10):
    """
    Fallback method: Fetches headlines from Yahoo Finance RSS Feed.
    """
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, features="xml")
    items = soup.findAll("item")[:max_articles]

    news = [(item.title.text, item.link.text) for item in items]
    return news


def analyze_sentiment(news_list):
    """
    Performs sentiment analysis on a list of (headline, url) tuples.
    Returns overall sentiment score and individual article scores.
    """
    sentiments = []
    for headline, url in news_list:
        result = sentiment_pipeline(headline)[0]
        score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
        sentiments.append((headline, url, score))

    overall_sentiment = sum(score for _, _, score in sentiments) / len(sentiments) if sentiments else 0
    return overall_sentiment, sentiments
