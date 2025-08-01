# your_project/app.py

import streamlit as st
import pandas as pd
import time
import os
import json
from typing import Optional

# Import custom modules from your project structure
from auths.auth import AuthManager
from core.data_fetcher import DataFetcher
from core.visualization import Visualization
from core.news_analyzer import NewsAnalyzer
from core.predictor import Predictor
from core.trading_engine import TradingEngine
from utils.session_utils import SessionManager
from db.user_manager import UserManager
from utils.formatting import Formatting
from utils.currency_converter import CurrencyConverter

# Suppress TensorFlow Logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize Managers
auth_manager = AuthManager()
data_fetcher = DataFetcher()
visualization = Visualization()
news_analyzer = NewsAnalyzer()
predictor = Predictor()
trading_engine = TradingEngine()
session_manager = SessionManager()
user_db = UserManager()

def load_css(file_name="styles.css"):
    css_path = os.path.join("static", file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_path}. Custom styles may not apply.")

st.set_page_config(layout="wide", page_title="AI Stock Advisor")
load_css()

def load_static_config(file_name="config.json"):
    config_path = os.path.join("static", file_name)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"Error decoding {file_name}: {e}")
            return {}
    return {}

static_ui_config = load_static_config()
app_name = static_ui_config.get("app_info", {}).get("app_name", "AI Stock Advisor")


def auth_sidebar_ui():
    st.sidebar.title("Account Access")
    if 'auth_page_selection' not in st.session_state:
        st.session_state['auth_page_selection'] = 'Login'
    auth_page_options = ["Login", "Sign Up", "Reset Password"]
    st.session_state['auth_page_selection'] = st.sidebar.radio(
        "Go to", auth_page_options, key="auth_page_radio", 
        index=auth_page_options.index(st.session_state['auth_page_selection'])
    )
    if st.session_state['auth_page_selection'] == "Login":
        auth_manager.login_ui()
    elif st.session_state['auth_page_selection'] == "Sign Up":
        auth_manager.signup_ui()
    elif st.session_state['auth_page_selection'] == "Reset Password":
        auth_manager.reset_password_ui()
    if session_manager.is_logged_in():
        st.rerun()

def main_app_ui():
    currency_converter = CurrencyConverter()

    st.sidebar.title(f"Welcome, {session_manager.get_current_user_email()}!")
    st.sidebar.write(f"Role: **{session_manager.get_current_user_role().capitalize()}**")
    if st.sidebar.button("Logout", key="sidebar_logout_button"):
        session_manager.logout_user()
        st.rerun()

    st.title(app_name)
    st.markdown("---")

    col_ticker, col_period, col_currency = st.columns([0.5, 0.25, 0.25])
    with col_ticker:
        ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, MSFT):", "AAPL", key="ticker_input").upper().strip()
    with col_period:
        period_options = {
            "1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
            "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "10 Years": "10y", "Year To Date": "ytd", "Max": "max"
        }
        selected_period_label = st.selectbox("Select Period", list(period_options.keys()), index=5, key="period_selector")
        historical_period = period_options[selected_period_label]
    with col_currency:
        supported_currencies = currency_converter.supported_currencies
        default_currency_index = supported_currencies.index("USD") if "USD" in supported_currencies else 0
        selected_currency = st.selectbox(
            "Display in Currency",
            supported_currencies,
            index=default_currency_index,
            key="currency_selector"
        )


    if st.button("Analyze Stock", use_container_width=True, key="analyze_button"):
        if not ticker_symbol:
            st.warning("Please enter a ticker symbol.")
            return

        st.subheader(f"Analysis for {ticker_symbol}")

        with st.spinner(f"Fetching historical data for the last {selected_period_label}..."):
            df = data_fetcher.fetch_historical_data(ticker_symbol, period=historical_period)
            if df.empty:
                st.error(f"Could not fetch data for {ticker_symbol}. Please check the ticker symbol or try again later.")
                user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_failed", f"Ticker: {ticker_symbol}, Period: {historical_period}")
                return
            user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_success", f"Ticker: {ticker_symbol}, Period: {historical_period}")
        
        conversion_rate = currency_converter.convert(1, selected_currency)
        currency_symbol = selected_currency if selected_currency != "USD" else "$"

        st.write("### Current Price Information")
        df_converted = df.copy()
        if conversion_rate is not None:
            df_converted[['Open', 'High', 'Low', 'Close']] *= conversion_rate
        else:
            st.warning("Could not fetch exchange rates. Displaying prices in USD.")
            currency_symbol = "$"

        col_open, col_close = st.columns(2)
        with col_open:
            st.metric(label=f"Current Open Price ({currency_symbol})", value=Formatting.format_currency(df_converted['Open'].iloc[-1], currency_symbol=currency_symbol))
        with col_close:
            st.metric(label=f"Current Close Price ({currency_symbol})", value=Formatting.format_currency(df_converted['Close'].iloc[-1], currency_symbol=currency_symbol))

        with st.spinner("Calculating technical indicators..."):
            df['RSI'] = data_fetcher.calculate_rsi(df)
            macd_df = data_fetcher.calculate_macd(df)
            df = df.join(macd_df)

        st.markdown("### Stock Charts")
        if session_manager.has_permission("view_charts_basic"):
            col_chart_static, col_chart_interactive = st.columns(2)
            with col_chart_static:
                st.write("#### Static Candlestick Chart (mplfinance)")
                fig_mpl = visualization.plot_candlestick(df_converted, f"{ticker_symbol} ({currency_symbol})")
                st.pyplot(fig_mpl)
            with col_chart_interactive:
                if session_manager.has_permission("view_charts_advanced"):
                    st.write("#### Interactive Candlestick Chart (Plotly)")
                    fig_plotly = visualization.plot_interactive_candlestick_plotly(df_converted, f"{ticker_symbol} ({currency_symbol})")
                    st.plotly_chart(fig_plotly, use_container_width=True)
                else:
                    st.info("Upgrade to a Premium plan for interactive charts with indicators.")
        else:
            st.info("Login or upgrade your plan to view stock charts.")

        st.markdown("### Latest News")
        if session_manager.has_permission("view_news_headlines"):
            with st.spinner("Fetching live news..."):
                news_articles = news_analyzer.get_news_headlines(ticker_symbol)
                st.session_state['news_sentiment'] = 'neutral'
                if news_articles:
                    for i, article in enumerate(news_articles):
                        st.markdown(f"**{i+1}. [{article.get('title', 'No Title')}]({article.get('url', '#')})**")
                        st.write(article.get('description', 'No description available.'))
                        if session_manager.has_permission("view_news_sentiment"):
                            sentiment = article.get('sentiment', 'N/A')
                            st.write(f"Sentiment: **{sentiment.capitalize()}**")
                            if sentiment == 'positive': st.session_state['news_sentiment'] = 'positive'
                            elif sentiment == 'negative': st.session_state['news_sentiment'] = 'negative'
                        published_at = article.get('publishedAt')
                        formatted_date = Formatting.format_date(pd.to_datetime(published_at), date_format="%Y-%m-%d %H:%M") if published_at and published_at != 'N/A' else 'N/A'
                        st.write(f"Source: {article.get('source', 'N/A')} | Published: {formatted_date}")
                        st.markdown("---")
                else:
                    st.info(f"No recent news found for {ticker_symbol}.")
                if not session_manager.has_permission("view_news_sentiment") and session_manager.has_permission("view_news_headlines"):
                    st.info("Upgrade to Premium to see news sentiment analysis.")
        else:
            st.info("Login or upgrade your plan to view live news.")
        
        st.markdown("### Future Price Prediction")
        predicted_prices_df = pd.DataFrame()
        if session_manager.has_permission("get_predictions"):
            with st.spinner("Predicting future prices..."):
                predictor.load_model()
                if predictor.model:
                    predicted_prices_df = predictor.predict_prices(df)
                    if not predicted_prices_df.empty:
                        st.write(f"Predicted Open and Close prices for the next few trading days in {selected_currency}:")
                        if conversion_rate is not None:
                            predicted_prices_df['Predicted Open'] *= conversion_rate
                            predicted_prices_df['Predicted Close'] *= conversion_rate
                        st.dataframe(predicted_prices_df.style.format(formatter=lambda x: f"{currency_symbol}{x:.2f}"), use_container_width=True)
                        st.plotly_chart(visualization.plot_prediction_chart(df, predicted_prices_df['Predicted Close']), use_container_width=True)
                        user_db._log_activity(session_manager.get_current_user_email(), "prediction_success", f"Ticker: {ticker_symbol}")
                    else:
                        st.warning("Could not generate price prediction. Ensure model is trained and data is sufficient.")
                        user_db._log_activity(session_manager.get_current_user_email(), "prediction_failed", f"Ticker: {ticker_symbol} - No prediction data.")
                else:
                    st.warning("Prediction model not available. Please ensure it is trained and loaded correctly.")
        else:
            st.info("Upgrade to a Premium plan to access AI-powered price predictions.")

        st.markdown("### Market Volatility")
        current_volatility = 0.0
        if session_manager.has_permission("view_volatility"):
            with st.spinner("Calculating market volatility..."):
                current_volatility = trading_engine.calculate_volatility(df['Close'])
                st.info(f"Current Annualized Volatility (last 20 days): **{Formatting.format_percentage(current_volatility)}**")
        else:
            st.info("Upgrade to Premium to view market volatility.")

        st.markdown("### Recommendation")
        if session_manager.has_permission("get_recommendations"):
            with st.spinner("Generating recommendation..."):
                if not predicted_prices_df.empty and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    predicted_close_price = predicted_prices_df['Predicted Close'].iloc[0]
                    recommendation = trading_engine.generate_recommendation(
                        predicted_price=predicted_close_price,
                        current_price=current_price,
                        volatility=current_volatility,
                        rsi=df['RSI'].iloc[-1] if not df['RSI'].isnull().all() else 50,
                        macd_diff=df['MACD_Diff'].iloc[-1] if 'MACD_Diff' in df.columns and not df['MACD_Diff'].isnull().all() else 0,
                        news_sentiment=st.session_state.get('news_sentiment', 'neutral')
                    )
                    if recommendation == "Buy":
                        st.success(f"**Recommendation: {recommendation}** - Strong indicators for potential growth.")
                    elif recommendation == "Sell":
                        st.error(f"**Recommendation: {recommendation}** - Indicators suggest potential decline.")
                    else:
                        st.warning(f"**Recommendation: {recommendation}** - Market conditions are uncertain or balanced, consider holding.")
                    user_db._log_activity(session_manager.get_current_user_email(), "recommendation_given", f"Ticker: {ticker_symbol}, Rec: {recommendation}")
                else:
                    st.warning("Cannot generate recommendation without prediction data.")
        else:
            st.info("Upgrade to a Premium plan to receive AI-powered Buy/Sell/Hold recommendations.")

if __name__ == "__main__":
    if not session_manager.is_logged_in():
        auth_sidebar_ui()
    else:
        main_app_ui()
