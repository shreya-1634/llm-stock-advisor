# your_project/core/trading_engine.py

import pandas as pd
import numpy as np
import math

class TradingEngine:
    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> float:
        """
        Calculates the annualized historical volatility (standard deviation of log returns).
        Args:
            prices (pd.Series): A pandas Series of closing prices.
            window (int): The number of periods to use for the rolling calculation.
        Returns:
            float: The latest annualized volatility. Returns 0.0 if not enough data.
        """
        if prices.empty or len(prices) < window + 1:
            print("Not enough data to calculate volatility.")
            return 0.0

        # Calculate daily log returns
        log_returns = np.log(prices / prices.shift(1)).dropna()
        
        if log_returns.empty or len(log_returns) < window:
             print("Not enough log returns to calculate rolling volatility.")
             return 0.0

        # Calculate rolling standard deviation and annualize
        # Assuming 252 trading days in a year for daily data
        volatility = log_returns.rolling(window=window).std() * np.sqrt(252)
        
        return volatility.iloc[-1] if not volatility.empty else 0.0

    def generate_recommendation(self, 
                                predicted_price: float, 
                                current_price: float, 
                                volatility: float, 
                                rsi: float, 
                                macd_diff: float, # MACD Histogram (MACD - Signal)
                                news_sentiment: str = "neutral",
                                price_change_threshold: float = 0.02, # 2% predicted change for strong signal
                                rsi_overbought: int = 70, 
                                rsi_oversold: int = 30) -> str:
        """
        Generates a Buy/Sell/Hold recommendation based on various factors.
        This is a simplified rule-based example; a real system might use a more complex model.
        
        Args:
            predicted_price (float): The predicted future price.
            current_price (float): The current stock price.
            volatility (float): The annualized historical volatility.
            rsi (float): The current Relative Strength Index.
            macd_diff (float): The MACD Histogram value (MACD - Signal Line).
            news_sentiment (str): Sentiment from news ('positive', 'negative', 'neutral').
            price_change_threshold (float): Percentage threshold for strong buy/sell based on prediction.
            rsi_overbought (int): RSI threshold for overbought condition.
            rsi_oversold (int): RSI threshold for oversold condition.
        Returns:
            str: "Buy", "Sell", or "Hold".
        """
        recommendation_score = 0 # Higher score for Buy, lower for Sell

        # 1. Price Prediction Factor
        if current_price > 0: # Avoid division by zero
            price_change_percent = (predicted_price - current_price) / current_price
            if price_change_percent > price_change_threshold:
                recommendation_score += 2 # Strong buy signal
            elif price_change_percent < -price_change_threshold:
                recommendation_score -= 2 # Strong sell signal
            else:
                # Moderate predicted change, slight influence
                recommendation_score += price_change_percent * 50 # Max 0.5 for 1% change

        # 2. RSI Factor
        if rsi < rsi_oversold:
            recommendation_score += 1 # Oversold, potential buy
        elif rsi > rsi_overbought:
            recommendation_score -= 1 # Overbought, potential sell

        # 3. MACD Factor (MACD Histogram)
        if macd_diff > 0: # MACD above signal line (bullish momentum)
            recommendation_score += 0.5
        elif macd_diff < 0: # MACD below signal line (bearish momentum)
            recommendation_score -= 0.5

        # 4. News Sentiment Factor
        if news_sentiment == "positive":
            recommendation_score += 1
        elif news_sentiment == "negative":
            recommendation_score -= 1

        # 5. Volatility Factor (Cautious in high volatility)
        # If volatility is very high, it might temper strong signals
        if volatility > 0.6: # Example threshold for very high volatility (annualized 60%)
            if abs(price_change_percent) < price_change_threshold * 2: # If prediction isn't super strong
                recommendation_score *= 0.7 # Reduce conviction

        # Final Recommendation based on aggregated score
        if recommendation_score >= 1.5:
            return "Buy"
        elif recommendation_score <= -1.5:
            return "Sell"
        else:
            return "Hold"
