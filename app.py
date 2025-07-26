# your_project/app.py

import streamlit as st
import pandas as pd
import time # For simulation of long processes

from auths.auth import AuthManager
from core.data_fetcher import DataFetcher
from core.visualization import Visualization
from core.news_analyzer import NewsAnalyzer
from core.predictor import Predictor
from core.trading_engine import TradingEngine
from utils.session_utils import SessionManager
from db.user_manager import UserManager # For potential admin features or logging


# Initialize managers
auth_manager = AuthManager()
data_fetcher = DataFetcher()
visualization = Visualization()
news_analyzer = NewsAnalyzer()
predictor = Predictor()
trading_engine = TradingEngine()
session_manager = SessionManager()
user_db = UserManager() # For logging and potential admin features

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title="AI Stock Advisor")

def auth_sidebar_ui():
    """Handles the authentication UI in the sidebar."""
    st.sidebar.title("Account Access")
    
    # Store the chosen page in session state to maintain selection across reruns
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

    # After any auth action, if logged in, rerun to clear auth forms and show main app
    if session_manager.is_logged_in():
        st.experimental_rerun()

def main_app_ui():
    """Main application UI visible after successful login."""
    st.sidebar.title(f"Welcome, {session_manager.get_current_user_email()}!")
    st.sidebar.write(f"Role: **{session_manager.get_current_user_role().capitalize()}**")
    if st.sidebar.button("Logout", key="sidebar_logout_button"):
        session_manager.logout_user()
        st.experimental_rerun()

    st.title("AI Stock Advisor")
    st.markdown("---")

    # Ticker input
    col_ticker, col_period = st.columns([0.7, 0.3])
    with col_ticker:
        ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, MSFT):", "AAPL", key="ticker_input").upper().strip()
    with col_period:
        # Define mapping for periods (yfinance compatible)
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
        selected_period_label = st.selectbox(
            "Select Period", 
            list(period_options.keys()), 
            index=5, # Default to "1 Year"
            key="period_selector"
        )
        historical_period = period_options[selected_period_label]


    if st.button("Analyze Stock", use_container_width=True, key="analyze_button"):
        if not ticker_symbol:
            st.warning("Please enter a ticker symbol.")
            return

        st.subheader(f"Analysis for {ticker_symbol}")

        # 1. Fetch Data
        with st.spinner(f"Fetching historical data for the last {selected_period_label}..."):
            df = data_fetcher.fetch_historical_data(ticker_symbol, period=historical_period)
            if df.empty:
                st.error(f"Could not fetch data for {ticker_symbol} for the period {selected_period_label}. Please check the ticker symbol or try again later.")
                user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_failed", f"Ticker: {ticker_symbol}, Period: {historical_period}")
                return
            user_db._log_activity(session_manager.get_current_user_email(), "data_fetch_success", f"Ticker: {ticker_symbol}, Period: {historical_period}")

        # 2. Calculate Indicators
        with st.spinner("Calculating technical indicators..."):
            df['RSI'] = data_fetcher.calculate_rsi(df)
            macd_df = data_fetcher.calculate_macd(df)
            df = df.join(macd_df)
            # You can add more indicators here like Bollinger Bands:
            # bb_df = data_fetcher.calculate_bollinger_bands(df)
            # df = df.join(bb_df)


        # 3. Display Charts (Permission-gated)
        st.markdown("### Stock Charts")
        if session_manager.has_permission("view_charts_basic"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("#### Static Candlestick Chart (mplfinance)")
                fig_mpl = visualization.plot_candlestick(df, ticker_symbol)
                st.pyplot(fig_mpl)
            with col2:
                if session_manager.has_permission("view_charts_advanced"):
                    st.write("#### Interactive Candlestick Chart (Plotly)")
                    fig_plotly = visualization.plot_interactive_candlestick_plotly(df, ticker_symbol)
                    st.plotly_chart(fig_plotly, use_container_width=True)
                else:
                    st.info("Upgrade to a Premium plan for interactive charts with indicators.")
        else:
            st.info("Login or upgrade your plan to view stock charts.")


        # 4. Fetch and Display News (Permission-gated)
        st.markdown("### Latest News")
        if session_manager.has_permission("view_news_headlines"):
            with st.spinner("Fetching live news..."):
                news_articles = news_analyzer.get_news_headlines(ticker_symbol)
                st.session_state['news_sentiment'] = 'neutral' # Initialize news sentiment

                if news_articles:
                    for i, article in enumerate(news_articles):
                        st.markdown(f"**{i+1}. [{article.get('title', 'No Title')}]({article.get('url', '#')})**")
                        st.write(article.get('description', 'No description available.'))
                        
                        if session_manager.has_permission("view_news_sentiment"):
                            st.write(f"Sentiment: **{article.get('sentiment', 'N/A').capitalize()}**")
                            # Simple aggregation for overall sentiment (can be improved)
                            if article.get('sentiment') == 'positive': st.session_state['news_sentiment'] = 'positive'
                            elif article.get('sentiment') == 'negative': st.session_state['news_sentiment'] = 'negative'
                        
                        st.write(f"Source: {article.get('source', 'N/A')} | Published: {pd.to_datetime(article.get('publishedAt')).strftime('%Y-%m-%d %H:%M') if article.get('publishedAt') and article.get('publishedAt') != 'N/A' else 'N/A'}")
                        st.markdown("---")
                else:
                    st.info(f"No recent news found for {ticker_symbol}.")
                
                if not session_manager.has_permission("view_news_sentiment") and session_manager.has_permission("view_news_headlines"):
                    st.info("Upgrade to Premium to see news sentiment analysis.")
        else:
            st.info("Login or upgrade your plan to view live news.")


        # 5. Predict Future Prices (Permission-gated)
        st.markdown("### Future Price Prediction")
        predicted_prices_series = pd.Series(dtype='float64') # Initialize empty series
        if session_manager.has_permission("get_predictions"):
            with st.spinner("Predicting future prices (this may take a moment, especially on first load)..."):
                # Ensure model is loaded (it will load if not already)
                predictor.load_model() 
                if predictor.model:
                    predicted_prices_series = predictor.predict_prices(df)
                    if not predicted_prices_series.empty:
                        st.write("Predicted prices for the next few trading days:")
                        st.plotly_chart(visualization.plot_prediction_chart(df, predicted_prices_series), use_container_width=True)
                        st.success(f"Predicted price for the next trading day: **${predicted_prices_series.iloc[0]:.2f}**")
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
                st.info(f"Current Annualized Volatility (last 20 days): **{current_volatility:.2f}**")
        else:
            st.info("Upgrade to Premium to view market volatility.")


        # 7. Buy/Sell/Hold Recommendation (Permission-gated)
        st.markdown("### Recommendation")
        if session_manager.has_permission("get_recommendations"):
            with st.spinner("Generating recommendation..."):
                if not predicted_prices_series.empty and not df.empty:
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
                    st.warning("Cannot generate recommendation without prediction data.")
        else:
            st.info("Upgrade to a Premium plan to receive AI-powered Buy/Sell/Hold recommendations.")

# --- Main Application Flow ---
if __name__ == "__main__":
    if not session_manager.is_logged_in():
        auth_sidebar_ui()
    else:
        main_app_ui()
