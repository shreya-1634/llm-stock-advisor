import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define thresholds for Buy/Sell/Hold
BUY_THRESHOLD = 1.02  # Predicted > 2% above current
SELL_THRESHOLD = 0.98  # Predicted < 2% below current

# Load model and initialize scaler
MODEL_PATH = "models/lstm_model.h5"
model = load_model(MODEL_PATH)

# Optional: load allowed users
def is_user_allowed(user_id: str):
    with open("auths/permissions.json", "r") as f:
        allowed = json.load(f)
    return user_id in allowed.get("permitted_users", [])


def download_data(ticker='AAPL', period='6mo', interval='1d'):
    df = yf.download(ticker, period=period, interval=interval)
    df.dropna(inplace=True)
    return df[['Close']]


def prepare_input_data(df, seq_len=60):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    X = []
    last_seq = scaled_data[-seq_len:]
    X.append(last_seq)
    X = np.array(X)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    return X, scaler


def make_prediction(ticker: str, user_id: str):
    # Check permissions
    if not is_user_allowed(user_id):
        return {
            "status": "error",
            "message": f"User '{user_id}' does not have AI execution permissions."
        }

    df = download_data(ticker)
    if len(df) < 60:
        return {
            "status": "error",
            "message": f"Not enough data to make a prediction for {ticker}"
        }

    X, scaler = prepare_input_data(df)
    prediction_scaled = model.predict(X)[0][0]
    prediction = scaler.inverse_transform([[prediction_scaled]])[0][0]

    current_price = df['Close'].iloc[-1]
    change_ratio = prediction / current_price

    # Generate recommendation
    if change_ratio > BUY_THRESHOLD:
        recommendation = "Buy"
    elif change_ratio < SELL_THRESHOLD:
        recommendation = "Sell"
    else:
        recommendation = "Hold"

    # Confidence: based on distance from thresholds
    diff = abs(change_ratio - 1)
    confidence = "High" if diff > 0.05 else "Moderate" if diff > 0.02 else "Low"

    return {
        "status": "success",
        "ticker": ticker.upper(),
        "predicted_price": round(prediction, 2),
        "current_price": round(current_price, 2),
        "recommendation": recommendation,
        "confidence": confidence
    }
