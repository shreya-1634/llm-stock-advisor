# 📈 LLM Stock Forecast Advisor

An AI-powered financial forecasting and decision-making assistant built using **LangChain**, **OpenAI GPT-4**, **Streamlit**, and **yfinance**. This project allows users to input any stock ticker (e.g., `TCS.NS`, `AAPL`, `RELIANCE.NS`) and receive a 10-day forecast, a recommended action (BUY/SELL/HOLD), and a natural language explanation — all powered by a large language model.

---

## 🚀 Features

- 🔍 Fetches the last 60 days of real-time stock prices
- 🤖 Uses **GPT-4** (via LangChain) to generate:
  - A price trend forecast
  - A recommended trading action
  - An explanation of the reasoning
- 📊 Built-in **Streamlit dashboard** for interactive use
- 📰 Accepts recent news headlines to inform decision-making
- ✅ Fully dynamic — works for any company/ticker from Yahoo Finance

---

## 🧠 Project Architecture

```plaintext
📥 Input: Stock Ticker + Optional News Headlines
⬇
📡 Fetch 60-day stock price history via yfinance
⬇
🧠 LangChain prompt template + GPT-4 reasoning
⬇
📤 Output:
    - 10-day forecast
    - BUY / SELL / HOLD
    - Natural language explanation
⬇
🌐 Display in Streamlit UI

---

## 📁 Folder Structure

```plaintext
llm-stock-advisor/
├── app/
│   ├── main.py         # Streamlit web interface
│   ├── utils.py        # yfinance data fetching
│   └── llm_chain.py    # LangChain LLM logic
├── .gitignore
├── requirements.txt    # Dependencies
└── README.md           # This file
