# your_project/app.py

import streamlit as st
import pandas as pd
import time # For simulating loading times or delays
import os   # For path handling
import json # For loading config.json

# Import custom modules from your project structure
from auths.auth import AuthManager
from core.data_fetcher import DataFetcher
from core.visualization import Visualization
from core.news_analyzer import NewsAnalyzer
from core.predictor import Predictor
from core.trading_engine import TradingEngine
from utils.session_utils import SessionManager
from db.user_manager import UserManager # Used for logging user activity
from utils.formatting import Formatting # For consistent data display


# --- Initialize Managers ---
# These instances will be used throughout the application to perform specific tasks.
auth_manager = AuthManager()
data_fetcher = DataFetcher()
visualization = Visualization()
news_analyzer = NewsAnalyzer()
predictor = Predictor()
trading_engine = TradingEngine()
session_manager = SessionManager()
user_db = UserManager() # Instance to interact with the user database (for logging etc.)


# --- Custom CSS Injection ---
# Function to load and inject custom CSS from static/styles.css
def load_css(file_name="styles.css"):
    css_path = os.path.join("static", file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_path}. Custom styles may not apply.")

# --- Static UI Configuration Loading ---
# Function to load UI configuration from static/config.json
def load_static_config(file_name="config.json"):
    config_path = os.path.join("static", file_name)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"Error decoding {file_name}: {e}")
            return {}
    return {} # Return empty dict if file not found

# --- Streamlit Page Configuration ---
# Set general page layout and title. This must be the first Streamlit command.
st.set_page_config(layout="wide", page_title="AI Stock Advisor")

# Load and apply custom CSS immediately after page configuration
load_css()

# Load static UI configuration (e.g., for dynamic text or colors in the app)
static_ui_config = load_static_config()
# Example of using static_ui_config (you can expand this as needed)
app_name = static_ui_config.get("app_info", {}).get("app_name", "AI Stock Advisor")


# --- Authentication UI Function ---
def auth_sidebar_ui():
    """
    Handles the authentication (Login, Sign Up, Reset Password) UI
    displayed in the Streamlit sidebar when a user is not logged in.
    """
    st.sidebar.title("Account Access")
    
    # Use session state to remember the last selected authentication page
    if 'auth_page_selection' not in st.session_state:
        st.session_state['auth_page_selection'] = 'Login'

    auth_page_options = ["Login", "Sign Up", "Reset Password"]
    st.session_state['auth_page_selection'] = st.sidebar.radio(
        "Go to", auth_page_options, key="auth_page_radio", 
        index=auth_page_options.index(st.session_state['auth_page_selection'])
    )

    # Display the selected authentication form
    if st.session_state['auth_page_selection'] == "Login":
        auth_manager.login_ui()
    elif st.session_state['auth_page_selection'] == "Sign Up":
        auth_manager.signup_ui()
    elif st.session_state['auth_page_selection'] == "Reset Password":
        auth_manager.reset_password_ui()

    # If a user successfully logs in/signs up, rerun the app to transition to the main UI
    if session_manager.is_logged_in():
        st.rerun()


# --- Main Application UI Function ---
def main_app_ui():
    """
    Contains the core functionality and UI elements of the AI Stock Advisor,
    displayed only after a user has successfully logged in.
    """
    # Display user info and logout button in the sidebar
    st.sidebar.title(f"Welcome, {session_manager.get_current_user_email()}!")
    st.sidebar.write(f"Role: **{session_manager.get_current_user_role().capitalize()}**")
    if st.sidebar.button("Logout", key="sidebar_logout_button"):
        session_manager.logout_user()
        st.rerun() # Rerun to go back to authentication screen

    st.title(app_name) # Use the app name from config.json
    st.markdown("---")

    # --- Ticker Input and Period Selection ---
    # Use columns for better layout of ticker input and period selection
    col_ticker, col_period = st.columns([0.7, 0.3])
    with col_ticker:
        ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, MSFT):", "AAPL", key="ticker_input").upper().strip()
    with col_period:
        # Define mapping for periods (compatible with yfinance)
        period_options = {
            "1 Day": "1d",
            "5 Days": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "10 Years": "10y",
            "Year To Date": "ytd",
            "Max": "max"
        }
        # Select box for period selection
        selected_period_label = st.selectbox(
            "Select Period", 
            list(period_options.keys()), 
            index=5, # Default to "1 Year"
            key="period_selector"
        )
        historical_period = period_options[selected_period_label] # Get the yfinance-compatible period string


    # --- Analyze Stock Button ---
    if st.button("Analyze Stock", use_container_width=True, key="analyze_button"):
        if not ticker_symbol:
            st.warning("Please enter a ticker symbol.")
            return

        st.subheader(f"Analysis for {ticker_symbol}")

        # 1. Fetch Historical Data
        with st.spinner(f"Fetching historical data for the last {selected_period_label}..."):
            df = data_fetcher.fetch_historical_data(ticker_symbol, period=historical_period)
            if df.empty:
                st.error(f"Could not fetch data for {ticker_symbol} for the period {selected_period_label}. "
                         "Please check the ticker symbol or try again later.")
                user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_failed", f"Ticker: {ticker_symbol}, Period: {historical_period}")
                return
            user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_success", f"Ticker: {ticker_symbol}, Period: {historical_period}")

        # 2. Calculate Technical Indicators (RSI, MACD)
        with st.spinner("Calculating technical indicators..."):
            df['RSI'] = data_fetcher.calculate_rsi(df)
            macd_df = data_fetcher.calculate_macd(df)
            df = df.join(macd_df) # Join MACD columns back to the main DataFrame
            # You can add more indicators here if desired (e.g., Bollinger Bands)
            # bb_df = data_fetcher.calculate_bollinger_bands(df)
            # df = df.join(bb_df)


        # 3. Display Stock Charts (Permission-gated)
        st.markdown("### Stock Charts")
        if session_manager.has_permission("view_charts_basic"):
            col_chart_static, col_chart_interactive = st.columns(2)
            with col_chart_static:
                st.write("#### Static Candlestick Chart (mplfinance)")
                fig_mpl = visualization.plot_candlestick(df, ticker_symbol)
                st.pyplot(fig_mpl) # Display matplotlib figure
            with col_chart_interactive:
                if session_manager.has_permission("view_charts_advanced"):
                    st.write("#### Interactive Candlestick Chart (Plotly)")
                    fig_plotly = visualization.plot_interactive_candlestick_plotly(df, ticker_symbol)
                    st.plotly_chart(fig_plotly, use_container_width=True) # Display Plotly figure
                else:
                    st.info("Upgrade to a Premium plan for interactive charts with indicators.")
        else:
            st.info("Login or upgrade your plan to view stock charts.")


        # 4. Fetch and Display Live News & Headlines (Permission-gated)
        st.markdown("### Latest News")
        if session_manager.has_permission("view_news_headlines"):
            with st.spinner("Fetching live news..."):
                news_articles = news_analyzer.get_news_headlines(ticker_symbol)
                # Initialize news sentiment for recommendation engine
                st.session_state['news_sentiment'] = 'neutral' 

                if news_articles:
                    for i, article in enumerate(news_articles):
                        st.markdown(f"**{i+1}. [{article.get('title', 'No Title')}]({article.get('url', '#')})**")
                        st.write(article.get('description', 'No description available.'))
                        
                        # Display news sentiment if user has permission
                        if session_manager.has_permission("view_news_sentiment"):
                            sentiment = article.get('sentiment', 'N/A')
                            st.write(f"Sentiment: **{sentiment.capitalize()}**")
                            # Simple aggregation for overall sentiment (can be improved)
                            if sentiment == 'positive': 
                                st.session_state['news_sentiment'] = 'positive'
                            elif sentiment == 'negative': 
                                st.session_state['news_sentiment'] = 'negative'
                        
                        # Format and display publication date using Formatting utility
                        published_at = article.get('publishedAt')
                        formatted_date = Formatting.format_date(pd.to_datetime(published_at), date_format="%Y-%m-%d %H:%M") if published_at and published_at != 'N/A' else 'N/A'
                        st.write(f"Source: {article.get('source', 'N/A')} | Published: {formatted_date}")
                        st.markdown("---")
                else:
                    st.info(f"No recent news found for {ticker_symbol}.")
                
                # Inform user about sentiment analysis if they don't have permission
                if not session_manager.has_permission("view_news_sentiment") and session_manager.has_permission("view_news_headlines"):
                    st.info("Upgrade to Premium to see news sentiment analysis.")
        else:
            st.info("Login or upgrade your plan to view live news.")


        # 5. Predict Future Prices (Permission-gated)
        st.markdown("### Future Price Prediction")
        predicted_prices_series = pd.Series(dtype='float64') # Initialize empty series
        if session_manager.has_permission("get_predictions"):
            with st.spinner("Predicting future prices (this may take a moment, especially on first load)..."):
                predictor.load_model() # Ensure model is loaded (it will load if not already)
                if predictor.model:
                    predicted_prices_series = predictor.predict_prices(df)
                    if not predicted_prices_series.empty:
                        st.write("Predicted prices for the next few trading days:")
                        st.plotly_chart(visualization.plot_prediction_chart(df, predicted_prices_series), use_container_width=True)
                        st.success(f"Predicted price for the next trading day: **{Formatting.format_currency(predicted_prices_series.iloc[0])}**")
                        user_db._log_activity(session_manager.get_current_user_email(), "prediction_success", f"Ticker: {ticker_symbol}")
                    else:
                        st.warning("Could not generate price prediction. Ensure model is trained and data is sufficient.")
                        user_db._log_activity(session_manager.get_current_user_email(), "prediction_failed", f"Ticker: {ticker_symbol} - Not enough data/model error.")
                else:
                    st.warning("Prediction model not available. Please ensure it is trained and loaded correctly.")
        else:
            st.info("Upgrade to a Premium plan to access AI-powered price predictions.")


        # 6. Calculate Market Volatility (Permission-gated)
        st.markdown("### Market Volatility")
        current_volatility = 0.0
        if session_manager.has_permission("view_volatility"):
            with st.spinner("Calculating market volatility..."):
                current_volatility = trading_engine.calculate_volatility(df['Close'])
                st.info(f"Current Annualized Volatility (last 20 days): **{Formatting.format_percentage(current_volatility)}**")
        else:
            st.info("Upgrade to Premium to view market volatility.")


        # 7. Buy/Sell/Hold Recommendation (Permission-gated)
        st.markdown("### Recommendation")
        if session_manager.has_permission("get_recommendations"):
            with st.spinner("Generating recommendation..."):
                # Ensure we have data for recommendation
                if not predicted_prices_series.empty and not df.empty and 'RSI' in df.columns and 'MACD_Diff' in df.columns:
                    recommendation = trading_engine.generate_recommendation(
                        predicted_price=predicted_prices_series.iloc[0],
                        current_price=df['Close'].iloc[-1],
                        volatility=current_volatility,
                        rsi=df['RSI'].iloc[-1] if not df['RSI'].isnull().all() else 50, # Default if NaN
                        macd_diff=df['MACD_Diff'].iloc[-1] if 'MACD_Diff' in df.columns and not df['MACD_Diff'].isnull().all() else 0, # Default if NaN
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
                    st.warning("Cannot generate recommendation without complete data (prediction, current price, indicators).")
        else:
            st.info("Upgrade to a Premium plan to receive AI-powered Buy/Sell/Hold recommendations.")


# --- Main Application Flow ---
# This block determines whether to show the authentication UI or the main app UI.
if __name__ == "__main__":
    if not session_manager.is_logged_in():
        auth_sidebar_ui() # Show authentication forms
    else:
        main_app_ui() # Show the main stock analysis application
