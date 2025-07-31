# your_project/core/predictor.py

import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from typing import Optional
import joblib # Ensure joblib is imported for scaler

class Predictor:
    def __init__(self):
        self.model_path = "data/model/lstm_model.h5"
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
            self.scaler = MinMaxScaler(feature_range=(0, 1)) # Fallback, but not ideal for prediction

    def load_model(self):
        """Loads the pre-trained LSTM model."""
        print(f"Attempting to load model from: {self.model_path}")
        if self.model is None: # Only try to load if not already loaded
            if os.path.exists(self.model_path):
                try:
                    self.model = tf.keras.models.load_model(self.model_path)
                    print("LSTM model loaded successfully.")
                except Exception as e:
                    print(f"ERROR: Failed to load LSTM model from {self.model_path}: {e}")
                    self.model = None
            else:
                print(f"WARNING: Model file not found at {self.model_path}. Please ensure it's trained and committed.")
                self.model = None
        else:
            print("Model already loaded.")

        self._load_scaler() # Ensure scaler is loaded when model is loaded

    def preprocess_data_for_prediction(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Preprocesses data for LSTM prediction.
        Scales the data and creates sequences.
        """
        if df.empty or 'Close' not in df.columns:
            print("DataFrame is empty or 'Close' column is missing for prediction preprocessing.")
            return None

        data = df['Close'].values.reshape(-1, 1)

        # If scaler is not loaded (e.g., first run without a saved scaler), fit it.
        # This is not ideal for production; ideally, the same scaler from training is used.
        if self.scaler is None:
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            self.scaler.fit(data) # Fit on available historical data
            # Optionally save scaler here for future use
            try:
                import joblib
                joblib.dump(self.scaler, self.scaler_path)
            except ImportError:
                pass # Joblib not installed

        scaled_data = self.scaler.transform(data)

        # Create input sequence for prediction (last `self.look_back` days)
        if len(scaled_data) < self.look_back:
            print(f"Not enough historical data ({len(scaled_data)} days) for prediction (need {self.look_back} days).")
            return None
            
        x_input = scaled_data[-self.look_back:]
        x_input = x_input.reshape(1, self.look_back, 1) # Reshape for LSTM: (samples, timesteps, features)
        return x_input

    def predict_prices(self, df: pd.DataFrame, num_predictions: int = 5) -> pd.DataFrame:
        """
        Generates a placeholder prediction for Open and Close prices.
        This function replaces the ML model's prediction logic for this deployment.
        The prediction is a simple linear extrapolation based on recent data.
        """
        if not self.model_available:
            if df.empty or len(df) < num_predictions:
                return pd.DataFrame()
            
            # Simple linear extrapolation for demonstration
            last_open = df['Open'].iloc[-1]
            last_close = df['Close'].iloc[-1]
            
            # Use average daily change from the last 5 days
            recent_changes = df[['Open', 'Close']].diff().dropna().tail(5).mean()
            open_change = recent_changes['Open']
            close_change = recent_changes['Close']
            
            predicted_data = []
            
            for i in range(1, num_predictions + 1):
                last_open += open_change
                last_close += close_change
                predicted_data.append([last_open, last_close])
            
            future_dates = pd.date_range(start=df.index[-1], periods=num_predictions + 1, freq='B')[1:]
            
            predicted_df = pd.DataFrame(predicted_data, index=future_dates, columns=['Predicted Open', 'Predicted Close'])
            return predicted_df
        
        return pd.DataFrame() # This return statement handles the case if a model were available and the next part of the logic was missing
