# your_project/auths/permissions.py

class Permissions:
    ROLES = {
        "guest": [], # Non-logged-in users (will still see upgrade messages or be redirected to login)
        "free": [
            "view_charts_basic",
            "view_charts_advanced", # Grant access to interactive charts
            "view_news_headlines",
            "view_news_sentiment",  # Grant access to news sentiment
            "get_predictions",      # Grant access to price predictions
            "get_recommendations",  # Grant access to buy/sell/hold recommendations
            "view_volatility"       # Grant access to market volatility
        ],
        "premium": [ # Keep premium role for future differentiation if needed, but it's now redundant for functionality
            "view_charts_basic",
            "view_charts_advanced",
            "view_news_headlines",
            "view_news_sentiment",
            "get_predictions",
            "get_recommendations",
            "view_volatility"
        ],
        "admin": [
            "view_charts_basic",
            "view_charts_advanced",
            "view_news_headlines",
            "view_news_sentiment",
            "get_predictions",
            "get_recommendations",
            "view_volatility",
            "manage_users" # Admin-specific permission
        ]
    }

    @staticmethod
    def check_permission(user_role: str, feature_name: str) -> bool:
        """
        Checks if a given user_role has access to a specific feature.
        """
        allowed_features = Permissions.ROLES.get(user_role, [])
        return feature_name in allowed_features
