import yfinance as yf
import requests

def fetch_recent_prices(ticker: str, days: int = 60):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if df.empty or "Close" not in df.columns:
            return None
        return df["Close"].tail(days).tolist()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def fetch_news_headlines(query, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])[:5]
        headlines = [f"- {a['title']}" for a in articles]
        return "\n".join(headlines)
    except Exception as e:
        print("❌ Error fetching news:", e)
        return "No major news reported."
