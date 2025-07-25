import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import os

scaler = MinMaxScaler(feature_range=(0, 1))

MODEL_PATH = "models/lstm_model.h5"  # Replace with your actual trained model path

def prepare_data(df, feature='Close', window_size=60):
    """
    Prepares scaled data for LSTM input.
    """
    data = df[feature].values.reshape(-1, 1)
    scaled_data = scaler.fit_transform(data)

    x_test = []
    for i in range(window_size, len(scaled_data)):
        x_test.append(scaled_data[i - window_size:i, 0])

    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    return x_test, scaled_data


def predict_future_price(df):
    """
    Loads pre-trained LSTM model and predicts next price based on recent data.
    """
    if not os.path.exists(MODEL_PATH):
        print("LSTM model not found. Returning last close price as fallback.")
        return df['Close'].iloc[-1]

    model = load_model(MODEL_PATH)
    x_test, scaled_data = prepare_data(df)

    predicted_price = model.predict(x_test)
    predicted_price = scaler.inverse_transform(predicted_price)
    
    return round(float(predicted_price[-1]), 2)


def calculate_volatility(df, period=14):
    """
    Computes rolling volatility (standard deviation of log returns).
    """
    df['Log Return'] = np.log(df['Close'] / df['Close'].shift(1))
    volatility = df['Log Return'].rolling(window=period).std() * np.sqrt(252)
    return round(float(volatility.iloc[-1]), 4)
