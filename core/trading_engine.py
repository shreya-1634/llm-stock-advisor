from core.config import get_logger
from core.data_fetcher import get_current_price
from auths.permissions import check_permission

logger = get_logger(__name__)

class TradingEngine:
    def __init__(self, balance=10000):
        self.balance = balance
        self.portfolio = {}  # Format: {'AAPL': {'quantity': 5, 'buy_price': 150}}
        logger.info("Trading Engine initialized")

    def buy_stock(self, ticker, quantity, user_permission_id=None):
        if user_permission_id and not check_permission(user_permission_id):
            logger.warning(f"Buy permission denied for: {user_permission_id}")
            return False, "Permission denied or expired."

        try:
            price = get_current_price(ticker)
            total_cost = price * quantity

            if total_cost > self.balance:
                logger.warning("Insufficient funds to buy")
                return False, "Insufficient funds."

            self.balance -= total_cost
            if ticker not in self.portfolio:
                self.portfolio[ticker] = {'quantity': quantity, 'buy_price': price}
            else:
                current = self.portfolio[ticker]
                new_qty = current['quantity'] + quantity
                avg_price = (current['buy_price'] * current['quantity'] + price * quantity) / new_qty
                self.portfolio[ticker] = {'quantity': new_qty, 'buy_price': avg_price}

            logger.info(f"Bought {quantity} of {ticker} at {price}")
            return True, f"Bought {quantity} shares of {ticker} at ${price:.2f}"

        except Exception as e:
            logger.error(f"Buy operation failed: {str(e)}")
            return False, "Buy operation failed."

    def sell_stock(self, ticker, quantity, user_permission_id=None):
        if user_permission_id and not check_permission(user_permission_id):
            logger.warning(f"Sell permission denied for: {user_permission_id}")
            return False, "Permission denied or expired."

        try:
            if ticker not in self.portfolio or self.portfolio[ticker]['quantity'] < quantity:
                logger.warning("Not enough shares to sell")
                return False, "Not enough shares to sell."

            price = get_current_price(ticker)
            total_revenue = price * quantity

            self.portfolio[ticker]['quantity'] -= quantity
            if self.portfolio[ticker]['quantity'] == 0:
                del self.portfolio[ticker]

            self.balance += total_revenue

            logger.info(f"Sold {quantity} of {ticker} at {price}")
            return True, f"Sold {quantity} shares of {ticker} at ${price:.2f}"

        except Exception as e:
            logger.error(f"Sell operation failed: {str(e)}")
            return False, "Sell operation failed."

    def get_portfolio(self):
        return self.portfolio

    def get_balance(self):
        return self.balance
