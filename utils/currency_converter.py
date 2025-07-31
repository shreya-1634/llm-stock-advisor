# your_project/utils/currency_converter.py

import requests
import os
import json
import time
from typing import Dict, Any, Optional

# A simple cache for exchange rates to avoid hitting the API on every app rerun
EXCHANGE_RATE_CACHE = {
    'rates': {},
    'timestamp': 0
}
CACHE_LIFETIME = 3600  # Cache for 1 hour (in seconds)

class CurrencyConverter:
    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_currency = "USD"
        
        # A hardcoded list of common currencies to display in the dropdown
        self.supported_currencies = [
            "USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", 
            "INR", "RUB", "BRL", "ZAR", "SGD", "NZD", "MXN", "AED"
        ]

    def _fetch_exchange_rates(self) -> Optional[Dict[str, float]]:
        """Fetches and caches the latest exchange rates from the API."""
        if not self.api_key:
            print("WARNING: EXCHANGE_RATE_API_KEY not set. Currency conversion disabled.")
            return None

        # Use cached data if available and not expired
        if time.time() - EXCHANGE_RATE_CACHE['timestamp'] < CACHE_LIFETIME:
            return EXCHANGE_RATE_CACHE['rates']

        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/{self.base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['result'] == 'success':
                EXCHANGE_RATE_CACHE['rates'] = data['conversion_rates']
                EXCHANGE_RATE_CACHE['timestamp'] = time.time()
                print("Successfully fetched and cached new exchange rates.")
                return EXCHANGE_RATE_CACHE['rates']
            else:
                print(f"API Error fetching exchange rates: {data.get('error-type', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching exchange rates: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def convert(self, amount: float, to_currency: str) -> Optional[float]:
        """Converts an amount from the base currency to a target currency."""
        rates = self._fetch_exchange_rates()
        if not rates or to_currency not in rates:
            return None
        
        rate = rates[to_currency]
        return amount * rate
