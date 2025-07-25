import os
import smtplib
import ssl
from email.message import EmailMessage
import openai
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

class APIManager:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.email_sender = os.getenv("EMAIL_SENDER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))

        # Setup OpenAI
        openai.api_key = self.openai_api_key

    # -------------------- OPENAI -------------------- #
    def get_openai_response(self, prompt, model="gpt-4", temperature=0.7):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return None

    # -------------------- NEWS API -------------------- #
    def get_news_headlines(self, ticker, num_articles=5):
        try:
            url = (
                f"https://newsapi.org/v2/everything?q={ticker}"
                f"&sortBy=publishedAt&language=en&pageSize={num_articles}&apiKey={self.news_api_key}"
            )
            response = requests.get(url)
            data = response.json()

            if data["status"] != "ok":
                print("[NewsAPI Error]", data)
                return []

            articles = [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"]
                }
                for article in data.get("articles", [])
            ]
            return articles
        except Exception as e:
            print(f"[NewsAPI Error] {e}")
            return []

    # -------------------- EMAIL OTP -------------------- #
    def send_email_otp(self, receiver_email, otp_code):
        try:
            subject = "Your OTP Code"
            body = f"Your verification code is: {otp_code}"
            em = EmailMessage()
            em["From"] = self.email_sender
            em["To"] = receiver_email
            em["Subject"] = subject
            em.set_content(body)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls(context=context)
                smtp.login(self.email_sender, self.email_password)
                smtp.send_message(em)
            return True
        except Exception as e:
            print(f"[Email OTP Error] {e}")
            return False
