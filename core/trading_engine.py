# your_project/core/trading_engine.py (UPDATED)

import pandas as pd
import numpy as np
import math

class TradingEngine:
    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> float:
        """
        Calculates the annualized historical volatility (standard deviation of log returns).
        """
        if prices.empty or len(prices) < window + 1:
            return 0.0

        log_returns = np.log(prices / prices.shift(1)).dropna()
        if log_returns.empty or len(log_returns) < window:
             return 0.0

        volatility = log_returns.rolling(window=window).std() * np.sqrt(252)
        return volatility.iloc[-1] if not volatility.empty else 0.0

    def generate_recommendation(self, 
                                predicted_close_price: float, 
                                current_close_price: float, 
                                volatility: float, 
                                rsi: float, 
                                macd_diff: float,
                                news_sentiment: str = "neutral",
                                price_change_threshold: float = 0.02,
                                rsi_overbought: int = 70, 
                                rsi_oversold: int = 30) -> str:
        """
        Generates a Buy/Sell/Hold recommendation based on various factors.
        This is a simplified rule-based example.
        """
        recommendation_score = 0
        price_change_percent = 0

        if current_close_price > 0:
            price_change_percent = (predicted_close_price - current_close_price) / current_close_price
            if price_change_percent > price_change_threshold:
                recommendation_score += 2
            elif price_change_percent < -price_change_threshold:
                recommendation_score -= 2
            else:
                recommendation_score += price_change_percent * 50

        if rsi < rsi_oversold and recommendation_score < 1.5:
            recommendation_score += 1
        elif rsi > rsi_overbought and recommendation_score > -1.5:
            recommendation_score -= 1

        if macd_diff > 0:
            recommendation_score += 0.5
        elif macd_diff < 0:
            recommendation_score -= 0.5

        if news_sentiment == "positive":
            recommendation_score += 1
        elif news_sentiment == "negative":
            recommendation_score -= 1

        if volatility > 0.6:
            if abs(price_change_percent) < price_change_threshold * 2:
                recommendation_score *= 0.7

        if recommendation_score >= 1.5:
            return "Buy"
        elif recommendation_score <= -1.5:
            return "Sell"
        else:
            return "Hold"
