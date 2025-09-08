# your_project/core/predictor.py

import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from typing import Optional
import joblib

class Predictor:
    def __init__(self):
        self.model_path = "data/model/generator_model.h5"
        self.scaler_path = "data/model/scaler.pkl"
        self.model = None
        self.scaler = None
        self.look_back = 60

    def _load_scaler(self):
        print(f"Attempting to load scaler from: {self.scaler_path}")
        if os.path.exists(self.scaler_path):
            try:
                self.scaler = joblib.load(self.scaler_path)
                print("Scaler loaded successfully.")
            except Exception as e:
                print(f"ERROR: Failed to load scaler from {self.scaler_path}: {e}")
                self.scaler = None
        else:
            print(f"WARNING: Scaler file not found at {self.scaler_path}.")
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            print("Using a new, unfitted scaler. Prediction results will be inaccurate until a model is trained.")

    def load_model(self):
        """Loads the pre-trained Generator model."""
        print(f"Attempting to load model from: {self.model_path}")
        if self.model is None:
            if os.path.exists(self.model_path):
                try:
                    self.model = tf.keras.models.load_model(self.model_path)
                    print("Generator model loaded successfully.")
                except Exception as e:
                    print(f"ERROR: Failed to load Generator model from {self.model_path}: {e}")
                    self.model = None
            else:
                print(f"WARNING: Model file not found at {self.model_path}. Please ensure it is trained and committed.")
                self.model = None
        else:
            print("Model already loaded.")
        
        self._load_scaler()

    def preprocess_data_for_prediction(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Preprocesses data for multivariate GAN prediction.
        """
        if df.empty or 'Open' not in df.columns or 'Close' not in df.columns:
            print("DataFrame is empty or 'Open'/'Close' columns are missing for prediction preprocessing.")
            return None

        data = df[['Open', 'Close']].values

        if self.scaler is None:
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            self.scaler.fit(data)
            try:
                joblib.dump(self.scaler, self.scaler_path)
            except ImportError:
                pass
            print("Scaler was not loaded, so a new one was fitted and saved.")

        scaled_data = self.scaler.transform(data)

        if len(scaled_data) < self.look_back:
            print(f"Not enough historical data ({len(scaled_data)} days) for prediction (need {self.look_back} days).")
            return None
            
        x_input = scaled_data[-self.look_back:]
        x_input = x_input.reshape(1, self.look_back, 2)
        return x_input

    def predict_prices(self, df: pd.DataFrame, num_predictions: int = 5) -> pd.DataFrame:
        """
        Predicts future Open and Close prices using the trained Generator model.
        """
        if self.model:
            x_input = self.preprocess_data_for_prediction(df)
            if x_input is None or x_input.size == 0:
                return pd.DataFrame()

            # The GAN generator needs a noise vector as input to generate new data
            noise = np.random.normal(0, 1, size=[1, self.look_back, 2])

            predicted_scaled_prices = self.model.predict(noise, verbose=0)
            
            # The GAN predicts the next day's price. We will repeat this to get multiple predictions.
            # This is a simplified approach for demonstration.
            predictions_list = predicted_scaled_prices.reshape(-1, 2)
            
            predicted_prices = self.scaler.inverse_transform(predictions_list)
            
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date, periods=num_predictions + 1, freq='B')[1:]
            
            predicted_df = pd.DataFrame(predicted_prices, index=future_dates, columns=['Predicted Open', 'Predicted Close'])
            return predicted_df
        
        else: # Placeholder logic if model is not loaded
            if df.empty or len(df) < 5:
                return pd.DataFrame()
            
            last_open = df['Open'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            
            recent_changes = df[['Open', 'Close']].diff().dropna().tail(5).mean()
            open_change = recent_changes['Open']
            close_change = recent_changes['Close']
            
            predicted_data = []
            
            for i in range(1, num_predictions + 1):
                open_price = last_open + open_change
                close_price = last_close + close_change
                predicted_data.append([open_price, close_price])
                last_open = open_price
                last_close = close_price

            future_dates = pd.date_range(start=df.index[-1], periods=num_predictions + 1, freq='B')[1:]
            
            predicted_df = pd.DataFrame(predicted_data, index=future_dates, columns=['Predicted Open', 'Predicted Close'])
            return predicted_df
