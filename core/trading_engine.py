import numpy as np
import pandas as pd
from core.data_fetcher import get_current_price
from datetime import datetime
from core.config import get_logger

logger = get_logger(__name__)

class TradingEngine:
    def __init__(self, username):
        self.username = username
        self.portfolio = {}
        self.trade_history = []
        logger.info(f"Trading engine created for {username}")

    def generate_recommendation(self, stock_data, news_articles=None):
        current_price = stock_data['Close'].iloc[-1]
        ma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
        
        delta = stock_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        sentiment_score = 0
        if news_articles:
            positive = sum(1 for a in news_articles if a['sentiment'] == 'POSITIVE')
            negative = sum(1 for a in news_articles if a['sentiment'] == 'NEGATIVE')
            sentiment_score = (positive - negative) / len(news_articles) if news_articles else 0
        
        recommendation = "HOLD"
        
        buy_signals = [
            current_price > ma_20 > ma_50,
            rsi < 70,
            sentiment_score > 0.2
        ]
        
        sell_signals = [
            current_price < ma_20 < ma_50,
            rsi > 30,
            sentiment_score < -0.2
        ]
        
        if all(buy_signals):
            recommendation = "BUY"
        elif all(sell_signals):
            recommendation = "SELL"
        
        logger.info(f"Generated recommendation: {recommendation}")
        return recommendation

    def execute_trade(self, action, ticker, quantity, price=None):
        trade_id = f"{action}-{ticker}-{datetime.now().timestamp()}"
        logger.info(f"Initiating trade {trade_id}")
        
        try:
            if not price:
                price = get_current_price(ticker)
            
            trade_value = price * quantity
            
            if action.upper() == "BUY":
                if ticker in self.portfolio:
                    self.portfolio[ticker]['quantity'] += quantity
                    self.portfolio[ticker]['avg_price'] = (
                        (self.portfolio[ticker]['avg_price'] * self.portfolio[ticker]['quantity'] + trade_value) / 
                        (self.portfolio[ticker]['quantity'] + quantity)
                    )
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
                    logger.warning(f"Insufficient holdings for {trade_id}")
                    return False
            
            self.trade_history.append({
                'timestamp': datetime.now(),
                'action': action,
                'ticker': ticker,
                'quantity': quantity,
                'price': price,
                'value': trade_value
            })
            
            logger.info(f"Trade {trade_id} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Trade {trade_id} failed: {str(e)}")
            return False

    def get_portfolio_value(self):
        total_value = 0
        for ticker, data in self.portfolio.items():
            try:
                current_price = get_current_price(ticker)
                total_value += current_price * data['quantity']
            except Exception as e:
                logger.warning(f"Couldn't value {ticker}: {str(e)}")
                continue
        return total_value
