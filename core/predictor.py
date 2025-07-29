# your_project/core/predictor.py

import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from typing import Optional

class Predictor:
    def __init__(self):
        self.model_path = "data/model/lstm_model.h5"
        self.scaler_path = "data/model/scaler.pkl" # To save/load the fitted scaler
        self.model = None
        self.scaler = None
        self.look_back = 60 # Number of past days to look at for prediction

    def _load_scaler(self):
        """Loads a pre-fitted MinMaxScaler."""
        # In a real application, you would save/load the scaler used during training
        # For simplicity in this conceptual code, we'll re-fit for prediction if not found
        # A more robust approach uses joblib or pickle to save/load the fitted scaler.
        try:
            import joblib
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print("Scaler loaded successfully.")
            else:
                print("Scaler not found. Will create a new one for prediction (might not be ideal).")
                self.scaler = MinMaxScaler(feature_range=(0, 1))
        except ImportError:
            print("Joblib not installed. Cannot load/save scaler. Using new MinMaxScaler for prediction.")
            self.scaler = MinMaxScaler(feature_range=(0, 1))


    def load_model(self):
        """Loads the pre-trained LSTM model."""
        if self.model is None and os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print("LSTM model loaded successfully.")
            except Exception as e:
                print(f"Error loading LSTM model from {self.model_path}: {e}")
                self.model = None
        elif not os.path.exists(self.model_path):
            print(f"Model not found at {self.model_path}. Please train the model first.")
        
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

    def predict_prices(self, df: pd.DataFrame, num_predictions: int = 5) -> pd.Series:
        """
        Predicts future stock prices for `num_predictions` days.
        Returns a Pandas Series of predicted prices.
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                print("Prediction aborted: LSTM model not loaded.")
                return pd.Series(dtype='float64')

        x_input = self.preprocess_data_for_prediction(df)
        if x_input is None or x_input.size == 0:
            return pd.Series(dtype='float64')

        predictions_list = []
        current_input = x_input

        for _ in range(num_predictions):
            predicted_scaled_price = self.model.predict(current_input, verbose=0)[0, 0]
            predictions_list.append(predicted_scaled_price)
            
            # Update input sequence: remove first element, add new prediction
            current_input = np.append(current_input[:, 1:, :], [[predicted_scaled_price]], axis=1)

        predicted_prices = self.scaler.inverse_transform(np.array(predictions_list).reshape(-1, 1))
        
        # Create a Series with future dates
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date, periods=num_predictions + 1, freq='B')[1:] # Exclude last known date, get business days
        
        return pd.Series(predicted_prices.flatten(), index=future_dates, name='Predicted Close')
