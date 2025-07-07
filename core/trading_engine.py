import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from core.data_fetcher import get_current_price
from core.news_analyzer import fetch_news
import yfinance as yf

class TradingEngine:
    def __init__(self, username):
        self.username = username
        self.portfolio = {}
        self.trade_history = []
    
    def generate_recommendation(self, stock_data, news_articles=None):
        """
        Generate buy/hold/sell recommendation based on technical and sentiment analysis
        """
        # Technical indicators
        current_price = stock_data['Close'].iloc[-1]
        ma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
        
        # Calculate RSI
        delta = stock_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Sentiment analysis
        sentiment_score = 0
        if news_articles:
            positive_news = sum(1 for article in news_articles if article['sentiment'] == 'POSITIVE')
            negative_news = sum(1 for article in news_articles if article['sentiment'] == 'NEGATIVE')
            sentiment_score = (positive_news - negative_news) / len(news_articles) if news_articles else 0
        
        # Generate recommendation
        recommendation = "HOLD"
        
        # Buy signal conditions
        if (current_price > ma_20 > ma_50 and 
            rsi < 70 and 
            sentiment_score > 0.2):
            recommendation = "BUY"
        
        # Sell signal conditions
        elif (current_price < ma_20 < ma_50 and 
              rsi > 30 and 
              sentiment_score < -0.2):
            recommendation = "SELL"
        
        return recommendation
    
    def execute_trade(self, action, ticker, quantity, price=None):
        """
        Execute a trade and update portfolio
        """
        if not price:
            price = get_current_price(ticker)
        
        timestamp = datetime.now()
        trade_value = price * quantity
        
        if action.upper() == "BUY":
            if ticker in self.portfolio:
                self.portfolio[ticker]['quantity'] += quantity
                self.portfolio[ticker]['avg_price'] = (
                    (self.portfolio[ticker]['avg_price'] * self.portfolio[ticker]['quantity'] + trade_value) / 
                    (self.portfolio[ticker]['quantity'] + quantity)
            else:
                self.portfolio[ticker] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'current_price': price
                }
        
        elif action.upper() == "SELL":
            if ticker in self.portfolio and self.portfolio[ticker]['quantity'] >= quantity:
                self.portfolio[ticker]['quantity'] -= quantity
                if self.portfolio[ticker]['quantity'] == 0:
                    del self.portfolio[ticker]
            else:
                return False
        
        # Record trade history
        self.trade_history.append({
            'timestamp': timestamp,
            'action': action,
            'ticker': ticker,
            'quantity': quantity,
            'price': price,
            'value': trade_value
        })
        
        return True
    
    def get_portfolio_value(self):
        """
        Calculate total portfolio value
        """
        total_value = 0
        for ticker, data in self.portfolio.items():
            current_price = get_current_price(ticker)
            total_value += current_price * data['quantity']
        return total_value
