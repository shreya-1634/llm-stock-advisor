# AI Stock Advisor

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow)
![SQLite](https://img.shields.io/badge/SQLite-DB-0769AD?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

## Table of Contents

- [AI Stock Advisor](#ai-stock-advisor)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Project Structure](#project-structure)
  - [Setup and Installation (Local)](#setup-and-installation-local)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Set Up Environment Variables](#4-set-up-environment-variables)
    - [5. Train the LSTM Model](#5-train-the-lstm-model)
  - [Running the Application (Local)](#running-the-application-local)
  - [Deployment](#deployment)
    - [Streamlit Community Cloud](#streamlit-community-cloud)
    - [Render](#render)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

---

## Introduction

The **AI Stock Advisor** is a powerful Streamlit web application designed to provide users with comprehensive stock analysis, real-time news, future price predictions, market volatility insights, and intelligent Buy/Sell/Hold recommendations. Leveraging machine learning (LSTM models) and various financial APIs, this tool aims to empower users with data-driven insights for better trading decisions.

The application features a robust authentication system with email verification and role-based access control, ensuring a personalized and secure user experience.

## Features

* **User Authentication:**
    * Secure Sign Up & Login with password hashing.
    * Email Verification via One-Time Passwords (OTP).
    * Password Reset functionality.
    * User activity logging.
* **Data Fetching:**
    * Live and historical stock price data (Open, High, Low, Close, Volume) using `yfinance`.
    * Dynamic period selection for charts (1d, 5d, 1mo, 6mo, 1y, etc., like Google Finance).
* **Technical Indicators:**
    * Correct calculation and display of Relative Strength Index (RSI).
    * Correct calculation and display of Moving Average Convergence Divergence (MACD).
* **Interactive Charts:**
    * Detailed Candlestick charts with overlaid indicators using `mplfinance` and `Plotly`.
    * Google Finance-like interactive charts for in-depth analysis.
* **Live News & Headlines:**
    * Fetches real-time news and headlines for the entered ticker symbol using NewsAPI.
    * Clickable links to read full articles from source websites.
    * Basic sentiment analysis of news articles.
* **Price Prediction:**
    * Predicts future stock prices for the ticker using a trained LSTM (Long Short-Term Memory) neural network model based on historical prices and news sentiment.
* **Market Volatility:**
    * Calculates and displays current market volatility.
* **Buy/Sell/Hold Recommendations:**
    * Provides AI-driven recommendations based on price predictions, technical indicators, news sentiment, and market volatility.
* **User Permission-driven AI Execution Flow:**
    * Features like price prediction and AI recommendations are gated based on user roles (e.g., 'Free' vs. 'Premium' users).

## Tech Stack

* **Frontend/Web Framework:** [Streamlit](https://streamlit.io/)
* **Backend/Core Logic:** Python 3.9+
* **Data Handling:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Stock Data:** [yfinance](https://pypi.org/project/yfinance/)
* **Technical Analysis:** [TA-Lib](https://technical-analysis-library-in-python.readthedocs.io/en/latest/) (via `ta` library)
* **Machine Learning:** [TensorFlow](https://www.tensorflow.org/) / [Keras](https://keras.io/) (for LSTM)
* **Data Preprocessing:** [Scikit-learn](https://scikit-learn.org/)
* **Database:** [SQLite3](https://docs.python.org/3/library/sqlite3.html) (for user management, activity logs, OTPs)
* **Password Hashing:** [Bcrypt](https://pypi.org/project/bcrypt/)
* **Email Sending:** Python's built-in `smtplib`
* **API Interactions:** [Requests](https://docs.python-requests.org/en/master/)
* **News API:** [NewsAPI.org](https://newsapi.org/)
* **Charting Libraries:** [Plotly](https://plotly.com/python/) (for interactive charts), [mplfinance](https://pypi.org/project/mplfinance/) (for static candlesticks)
* **Environment Variables:** [python-dotenv](https://pypi.org/project/python-dotenv/)
* **Testing:** [Pytest](https://pytest.org/), [pytest-mock](https://pypi.org/project/pytest-mock/)

## Project Structure

The project follows a modular and organized structure to separate concerns:

```

your_project/
├── app.py                         \# Main Streamlit application
├── .env                           \# Environment variables (API keys, DB creds) - KEEP LOCAL
├── runtime.txt                    \# Python runtime version (e.g., for Heroku/Render)
├── requirements.txt               \# Python dependencies
├── README.md                      \# Project overview
├── Procfile                       \# Render/Heroku web service startup command

├── .streamlit/                    \# Streamlit specific config (optional, for secrets.toml if used)
│   └── secrets.toml               \# Streamlit Cloud secrets - KEEP LOCAL

├── auths/                         \# Authentication related modules
│   ├── **init**.py
│   ├── auth.py                    \# Signup/login/email verify/reset logic
│   └── permissions.py             \# Role-based access logic

├── core/                          \# Core application logic and integrations
│   ├── **init**.py
│   ├── api\_manager.py             \# External API interfaces (NewsAPI etc.)
│   ├── config.py                  \# Global constants
│   ├── data\_fetcher.py            \# Stock prices, RSI, MACD fetching
│   ├── news\_analyzer.py           \# News sentiment, summaries
│   ├── predictor.py               \# Loads & uses LSTM model for predictions
│   ├── trading\_engine.py          \# Buy/Sell/Hold + Volatility calculation
│   └── visualization.py           \# Chart rendering (candles, RSI, MACD, predictions)

├── data/                          \# Data storage (cached, generated models)
│   ├── **init**.py
│   ├── ticker\_cache/              \# Cached historical data for tickers (e.g., AAPL\_1y.csv)
│   └── model/                     \# Trained ML models and scalers
│       ├── lstm\_model.h5          \# Trained price predictor model
│       └── scaler.pkl             \# Fitted data scaler for ML model

├── db/                            \# Database interaction layer
│   ├── **init**.py
│   └── user\_manager.py            \# User handling logic (CRUD on SQLite, OTP, logs)

├── static/                        \# Static assets for UI
│   ├── **init**.py
│   ├── config.json                \# UI layout, theme config
│   └── styles.css                 \# Custom CSS styling

├── utils/                         \# Reusable utility functions
│   ├── **init**.py
│   ├── email\_utils.py             \# OTPs, email sending
│   ├── password\_utils.py          \# Hashing & verification
│   ├── session\_utils.py           \# Manage Streamlit sessions
│   └── formatting.py              \# Format prices, charts, etc.

├── scripts/                       \# Standalone scripts (e.g., for model training)
│   └── train\_model.py             \# Train & export `lstm_model.h5`

├── tests/                         \# Unit and integration tests
│   ├── **init**.py
│   ├── test\_auth.py
│   ├── test\_data\_fetcher.py
│   ├── test\_permissions.py
│   └── test\_predictor.py

````

## Setup and Installation (Local)

Follow these steps to set up and run the AI Stock Advisor on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-github-username/your-repo-name.git](https://github.com/your-github-username/your-repo-name.git)
cd your-repo-name
````

### 2\. Create and Activate Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3\. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 4\. Set Up Environment Variables

Create a file named `.env` in the root directory of your project (same level as `app.py`). This file will store your API keys and sensitive credentials. **Do NOT commit this file to GitHub.**

```
# .env

# NewsAPI Key (Get one from [https://newsapi.org/](https://newsapi.org/))
NEWS_API_KEY=your_news_api_key_here

# Alpha Vantage API Key (Optional, if yfinance isn't enough. Get one from [https://www.alphavantage.co/](https://www.alphavantage.co/))
# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Email Server Settings for OTP/Password Reset
# Example for Gmail (you might need to enable "App Passwords" for your Google account)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_app_password # Use an App Password for Gmail

# Secret key for Streamlit session management (generate a strong random string)
# You can generate one in Python: import secrets; print(secrets.token_hex(32))
SESSION_SECRET_KEY=a_long_random_string_for_streamlit_session_state
```

### 5\. Train the LSTM Model

The price prediction feature relies on a pre-trained LSTM model. You need to train and save this model once.

```bash
python scripts/train_model.py
```

This script will:

  * Fetch historical data for `AAPL` (default) for 5 years.
  * Preprocess the data.
  * Train the LSTM model.
  * Save the trained model (`lstm_model.h5`) and the data scaler (`scaler.pkl`) into the `data/model/` directory.

## Running the Application (Local)

Once all dependencies are installed and the model is trained, you can run the Streamlit application:

```bash
streamlit run app.py
```

This will open the application in your web browser, usually at `http://localhost:8501`.

## Deployment

### Streamlit Community Cloud

The easiest way to deploy your Streamlit app for free.

1.  **Ensure `secrets.toml` is set up:**
      * Create a `.streamlit/` directory at your project root.
      * Create a `secrets.toml` file inside it (e.g., `.streamlit/secrets.toml`).
      * Populate `secrets.toml` with your API keys and credentials, using the TOML format. **Do NOT commit `secrets.toml` to GitHub.** Add `.streamlit/secrets.toml` to your `.gitignore`.
      * Update `api_manager.py`, `email_utils.py`, `session_utils.py` to use `st.secrets.get("KEY_NAME")` instead of `os.getenv("KEY_NAME")`.
2.  **Go to [Streamlit Cloud](https://share.streamlit.io/)**, click "New app", connect your GitHub repository, select the branch and `app.py` file.
3.  **Database Persistence:** On Streamlit Cloud, the file system is ephemeral. Your `data/users.db` SQLite database will be reset on each app restart. For persistent user data, consider using Streamlit's native connections for external databases (like PostgreSQL/MySQL) or a service like Firebase Firestore/Supabase.

### Render

A powerful cloud platform that offers a free tier for web services.

1.  **Ensure `Procfile` is in root:** As discussed, create `Procfile` (no extension) in your root directory with:
    ```
    web: streamlit run app.py --server.port $PORT --server.enableCORS false --server.enableXsrfProtection false
    ```
2.  **Ensure `requirements.txt` is complete.**
3.  **Go to [Render.com](https://render.com/)**, log in, and create a "New Web Service".
4.  **Connect your GitHub repository.**
5.  **Configure:** Provide a name, select Python 3 runtime, set `Build Command` to `pip install -r requirements.txt`, and ensure `Start Command` matches your `Procfile` entry.
6.  **Add Environment Variables:** Crucially, copy all your secrets (API keys, email credentials, `SESSION_SECRET_KEY`) from your local `.env` file directly into Render's "Environment Variables" section during configuration. Render does not automatically read `.env` or `secrets.toml`.
7.  **Database Persistence:** Similar to Streamlit Cloud, `data/users.db` will not persist across deployments or app restarts on Render's free tier. Consider using a Render PostgreSQL service (paid) or an external database for persistent user data.

## Contributing

Contributions are welcome\! If you have suggestions for improvements, bug fixes, or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## Contact

For any questions or inquiries, please contact:

  * Shreya Priyadrshni
  * shreyamgm16@gmail.com
  * https://github.com/shreya-1634
