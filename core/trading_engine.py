from core.data_fetcher import get_current_price
from datetime import datetime
import numpy as np
import pandas as pd
import traceback
from core.config import get_logger

logger = get_logger(__name__)

class TradingEngine:
    def __init__(self, username):
        self.username = username
        self.portfolio = {}
        self.trade_history = []
        logger.info(f"TradingEngine created for {username}")

    def generate_recommendation(self, stock_data, news_articles=None):
        try:
            logger.debug("Generating trade recommendation")
            current_price = stock_data['Close'].iloc[-1]
            ma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
            
            # RSI calculation
            delta = stock_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # Sentiment analysis
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
            
            logger.info(f"Recommendation generated: {recommendation}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}\n{traceback.format_exc()}")
            return "HOLD"

    def execute_trade(self, action, ticker, quantity, price=None):
        trade_id = f"{action}-{ticker}-{datetime.now().timestamp()}"
        logger.info(f"Trade {trade_id} initiated")
        
        try:
            if not price:
                logger.debug("Fetching current price")
                price = get_current_price(ticker)
            
            trade_value = price * quantity
            timestamp = datetime.now()
            
            if action.upper() == "BUY":
                logger.debug(f"Processing BUY order for {ticker}")
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
                logger.debug(f"Processing SELL order for {ticker}")
                if ticker in self.portfolio and self.portfolio[ticker]['quantity'] >= quantity:
                    self.portfolio[ticker]['quantity'] -= quantity
                    if self.portfolio[ticker]['quantity'] == 0:
                        del self.portfolio[ticker]
                else:
                    logger.warning(f"Insufficient holdings for SELL: {ticker}")
                    return False
            
            # Record trade
            self.trade_history.append({
                'timestamp': timestamp,
                'action': action,
                'ticker': ticker,
                'quantity': quantity,
                'price': price,
                'value': trade_value
            })
            
            logger.info(f"Trade {trade_id} executed: {action} {quantity} {ticker} @ {price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Trade {trade_id} failed: {str(e)}\n{traceback.format_exc()}")
            return False

    def get_portfolio_value(self):
        try:
            total_value = 0
            for ticker, data in self.portfolio.items():
                current_price = get_current_price(ticker)
                total_value += current_price * data['quantity']
            logger.debug(f"Portfolio value calculated: ${total_value:.2f}")
            return total_value
        except Exception as e:
            logger.error(f"Portfolio valuation failed: {str(e)}")
            return 0
