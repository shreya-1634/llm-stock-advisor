# your_project/utils/formatting.py

import pandas as pd

class Formatting:
    @staticmethod
    def format_currency(amount: float, currency_symbol: str = "$", decimal_places: int = 2) -> str:
        """Formats a float as a currency string."""
        return f"{currency_symbol}{amount:,.{decimal_places}f}"

    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """Formats a float as a percentage string (e.g., 0.15 -> '15.00%')."""
        return f"{value * 100:.{decimal_places}f}%"

    @staticmethod
    def format_date(date_obj: pd.Timestamp, date_format: str = "%Y-%m-%d") -> str:
        """Formats a pandas Timestamp object to a string."""
        if pd.isna(date_obj):
            return "N/A"
        return date_obj.strftime(date_format)

    @staticmethod
    def format_volume(volume: int) -> str:
        """Formats a large volume number for readability (e.g., 1234567 -> '1.23M')."""
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.2f}K"
        else:
            return str(volume)

    @staticmethod
    def round_float(value: float, decimal_places: int = 2) -> float:
        """Rounds a float to a specified number of decimal places."""
        return round(value, decimal_places)
