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

    def calculate_indicators(self, stock_data):
        indicators = {}

        # Moving Averages
        indicators['ma_20'] = stock_data['Close'].rolling(window=20).mean().iloc[-1]
        indicators['ma_50'] = stock_data['Close'].rolling(window=50).mean().iloc[-1]

        # RSI (Relative Strength Index)
        delta = stock_data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))

        return indicators

    def generate_recommendation(self, stock_data, news_articles=None):
        current_price = stock_data['Close'].iloc[-1]
        indicators = self.calculate_indicators(stock_data)

        ma_signal = 0
        if current_price > indicators['ma_20'] > indicators['ma_50']:
            ma_signal = 1
        elif current_price < indicators['ma_20'] < indicators['ma_50']:
            ma_signal = -1

        rsi_signal = 0
        if indicators['rsi'] < 30:
            rsi_signal = 1
        elif indicators['rsi'] > 70:
            rsi_signal = -1

        sentiment_score = 0
        if news_articles:
            positive = sum(1 for a in news_articles if a['sentiment'].lower() == 'positive')
            negative = sum(1 for a in news_articles if a['sentiment'].lower() == 'negative')
            sentiment_score = (positive - negative) / len(news_articles)
        sentiment_signal = 1 if sentiment_score > 0.2 else -1 if sentiment_score < -0.2 else 0

        score = ma_signal + rsi_signal + sentiment_signal

        if score >= 2:
            recommendation = "BUY"
        elif score <= -2:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"

        return {
            "recommendation": recommendation,
            "indicators": {
                "MA Signal": ma_signal,
                "RSI Signal": rsi_signal,
                "Sentiment Signal": sentiment_signal
            }
        }

    def execute_trade(self, action, ticker, quantity, price=None):
        trade_id = f"{action}-{ticker}-{datetime.now().timestamp()}"
        logger.info(f"Initiating trade {trade_id}")
        try:
            if not price:
                price = get_current_price(ticker)

            trade_value = price * quantity

            if action.upper() == "BUY":
                if ticker in self.portfolio:
                    prev_qty = self.portfolio[ticker]['quantity']
                    prev_avg = self.portfolio[ticker]['avg_price']
                    new_qty = prev_qty + quantity
                    new_avg = ((prev_avg * prev_qty) + trade_value) / new_qty
                    self.portfolio[ticker]['quantity'] = new_qty
                    self.portfolio[ticker]['avg_price'] = new_avg
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
