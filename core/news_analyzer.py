# your_project/core/news_analyzer.py

from core.api_manager import APIManager
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Download VADER lexicon for sentiment analysis if not already downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
# Original: except nltk.downloader.DownloadError:
except Exception: # <--- CHANGE THIS LINE TO CATCH A GENERAL EXCEPTION
    print("VADER lexicon not found, attempting to download...")
    try:
        nltk.download('vader_lexicon')
        print("VADER lexicon downloaded successfully.")
    except Exception as e:
        print(f"Error downloading VADER lexicon: {e}")
        print("Sentiment analysis may not work correctly.")

class NewsAnalyzer:
    def __init__(self):
        self.api_manager = APIManager()
        self.sid = SentimentIntensityAnalyzer()

    def get_news_headlines(self, query: str, limit: int = 5) -> list:
        """
        Fetches news articles for a given query (e.g., ticker symbol)
        and returns a list of dictionaries with relevant news details.
        """
        # Refine the query for better results if needed
        articles = self.api_manager.fetch_news_articles(query, limit)
        
        processed_articles = []
        for article in articles:
            processed_articles.append({
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No description available.'),
                'url': article.get('url', '#'),
                'source': article.get('source', {}).get('name', 'N/A'),
                'publishedAt': article.get('publishedAt', 'N/A'),
                'sentiment': self.analyze_sentiment(article.get('title', '') + " " + article.get('description', ''))
            })
        return processed_articles

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyzes the sentiment of a given text using VADER.
        Returns 'positive', 'negative', or 'neutral'.
        """
        if not text:
            return "neutral"
        scores = self.sid.polarity_scores(text)
        compound_score = scores['compound']
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
