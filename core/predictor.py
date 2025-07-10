import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import json
import os
from .config import get_logger

logger = get_logger(__name__)

class LSTMPredictor:
    def __init__(self):
        with open("static/config.json") as f:
            self.config = json.load(f)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        logger.info("LSTM Predictor initialized")

    def prepare_data(self, data):
        window_size = self.config["MODEL"]["TRAINING_WINDOW"]
        close_prices = data['Close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(close_prices)
        
        X, y = [], []
        for i in range(window_size, len(scaled_data)):
            X.append(scaled_data[i-window_size:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X, y

    def build_model(self, input_shape):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.3),
            LSTM(64, return_sequences=False),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        logger.debug("Model architecture built")
        return model

    def train_and_save_model(self, data, model_path="models/lstm_model.h5"):
        X, y = self.prepare_data(data)
        model = self.build_model((X.shape[1], 1))
        
        logger.info("Starting model training...")
        model.fit(
            X, y,
            epochs=self.config["MODEL"]["EPOCHS"],
            batch_size=self.config["MODEL"]["BATCH_SIZE"],
            callbacks=[EarlyStopping(monitor='loss', patience=5)],
            verbose=1
        )
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        logger.info(f"Model saved to {model_path}")
        return model

    def load_model(self, model_path="models/lstm_model.h5"):
        if os.path.exists(model_path):
            logger.debug(f"Loading model from {model_path}")
            return load_model(model_path)
        raise FileNotFoundError(f"Model file not found at {model_path}")

    def predict(self, data, days=7):
        model = self.load_model()
        window_size = self.config["MODEL"]["TRAINING_WINDOW"]
        
        close_prices = data['Close'].values[-window_size:]
        scaled_prices = self.scaler.transform(close_prices.reshape(-1, 1))
        
        predictions = []
        current_sequence = scaled_prices.reshape(1, window_size, 1)
        
        logger.info(f"Predicting next {days} days")
        for _ in range(days):
            next_pred = model.predict(current_sequence, verbose=0)[0, 0]
            predictions.append(next_pred)
            current_sequence = np.append(
                current_sequence[:, 1:, :],
                [[[next_pred]]],
                axis=1
            )
        
        predictions = self.scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        )
        
        last_date = data.index[-1]
        future_dates = pd.date_range(
            start=last_date,
            periods=days + 1,
            freq='B'
        )[1:]
        
        return pd.DataFrame({
            'Date': future_dates,
            'Close': predictions.flatten()
        }).set_index('Date')

stock_predictor = LSTMPredictor()

def predict_future_prices(data, days=7):
    return stock_predictor.predict(data, days)
