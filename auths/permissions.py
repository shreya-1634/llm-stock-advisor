# your_project/auths/permissions.py

class Permissions:
    ROLES = {
        "guest": [], 
        "free": [
            "view_charts_basic",
            "view_charts_advanced",
            "view_news_headlines",
            "view_news_sentiment",
            "get_predictions",
            "get_recommendations",
            "view_volatility"
        ],
        "premium": [
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
            "manage_users"
        ]
    }

    @staticmethod
    def check_permission(user_role: str, feature_name: str) -> bool:
        """
        Checks if a given user_role has access to a specific feature.
        """
        allowed_features = Permissions.ROLES.get(user_role, [])
        return feature_name in allowed_features
