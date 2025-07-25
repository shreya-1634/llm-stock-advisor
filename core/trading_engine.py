import logging
from core.predictor import predict_price_and_volatility
from core.news_analyzer import analyze_sentiment

logger = logging.getLogger(__name__)

def calculate_trading_decision(ticker: str, df, news_headlines, allow_ai_trade: bool = False):
    """
    Determines Buy/Sell/Hold recommendation and executes decision if allowed.
    """

    try:
        # Get price prediction and volatility estimate
        predicted_price, current_price, volatility = predict_price_and_volatility(ticker, df)

        # Sentiment from news headlines
        sentiment_score = analyze_sentiment(news_headlines)

        logger.info(f"[{ticker}] Predicted Price: {predicted_price:.2f}, "
                    f"Current: {current_price:.2f}, Volatility: {volatility:.4f}, "
                    f"Sentiment: {sentiment_score:.2f}")

        decision = "Hold"

        # Basic recommendation logic
        price_diff_percent = ((predicted_price - current_price) / current_price) * 100

        if price_diff_percent > 3 and sentiment_score > 0:
            decision = "Buy"
        elif price_diff_percent < -3 and sentiment_score < 0:
            decision = "Sell"
        else:
            decision = "Hold"

        action_executed = None

        if allow_ai_trade:
            action_executed = execute_trade(decision, ticker)
        else:
            logger.info(f"AI recommends to: {decision}, but waiting for user permission.")

        return {
            "ticker": ticker,
            "predicted_price": predicted_price,
            "current_price": current_price,
            "volatility": volatility,
            "sentiment_score": sentiment_score,
            "recommendation": decision,
            "executed": action_executed
        }

    except Exception as e:
        logger.error(f"Error in trading decision for {ticker}: {str(e)}")
        return {
            "error": f"Could not evaluate decision for {ticker}"
        }


def execute_trade(decision: str, ticker: str):
    """
    Mock trading execution logic. In a real system, this would be a broker API call.
    """
    logger.info(f"[EXECUTING TRADE] Decision: {decision} on {ticker}")

    # Simulated execution
    return f"{decision} executed on {ticker}"
