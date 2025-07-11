import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from .data_fetcher import get_current_price
from .config import get_logger

logger = get_logger(__name__)

class TradingEngine:
    def __init__(self, username):
        if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
            st.warning("🔐 Please login to access trading engine.")
            st.stop()

        self.username = username
        self.portfolio = {}
        self.trade_history = []
        logger.info(f"Trading engine initialized for {username}")

    
    def generate_recommendation(self, data: pd.DataFrame, news: list):
        if data.empty:
            return "HOLD"

        price = data["Close"].iloc[-1]
        ma20 = data["Close"].rolling(20).mean().iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]

        delta = data["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        sentiment = 0
        if news:
            pos = sum(1 for a in news if a["sentiment"] == "POSITIVE")
            neg = sum(1 for a in news if a["sentiment"] == "NEGATIVE")
            sentiment = (pos - neg) / len(news)

        buy = price > ma20 > ma50 and rsi < 70 and sentiment > 0.2
        sell = price < ma20 < ma50 and rsi > 30 and sentiment < -0.2

        if buy:
            return "BUY"
        if sell:
            return "SELL"
        return "HOLD"

    def execute_trade(self, action, ticker, quantity, price=None):
        if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
            st.warning("🔐 Please login to execute trades.")
            return False

        trade_id = f"{action}-{ticker}-{datetime.now().timestamp()}"
        logger.info(f"Executing trade {trade_id}")

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
                    logger.warning("❌ Insufficient holdings.")
                    return False

            self.trade_history.append({
                'timestamp': datetime.now(),
                'action': action,
                'ticker': ticker,
                'quantity': quantity,
                'price': price,
                'value': trade_value
            })

            logger.info(f"Trade {trade_id} executed.")
            return True

        except Exception as e:
            logger.error(f"Trade execution failed: {str(e)}")
            return False

    def get_portfolio_value(self):
        total_value = 0
        for ticker, data in self.portfolio.items():
            try:
                current_price = get_current_price(ticker)
                total_value += current_price * data['quantity']
            except Exception as e:
                logger.warning(f"Error valuing {ticker}: {str(e)}")
                continue
        return total_value
