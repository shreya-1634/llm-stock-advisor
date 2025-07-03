import yfinance as yf
import requests
import pandas as pd
from langchain_community.document_loaders import WebBaseLoader

def fetch_all_prices(ticker: str):
    try:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=True)
        return df["Close"] if not df.empty else None
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return None

def fetch_news_with_llm(query: str):
    search_urls = [
        f"https://www.google.com/search?q={query}+stock+news",
        f"https://finance.yahoo.com/quote/{query}",
        f"https://www.reuters.com/companies/{query}",
    ]

    headlines = []
    for url in search_urls:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            headlines.append(docs[0].page_content[:500])
        except Exception as e:
            print(f"⚠️ Skipped {url} due to error.")
            continue

    return "\n\n".join(headlines[:3]) if headlines else "No news found."

def calculate_volatility(prices: pd.Series, window: int = 30):
    return prices.pct_change().rolling(window).std().dropna()
