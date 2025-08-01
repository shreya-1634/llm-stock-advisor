# your_project/scripts/train_model.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import joblib
from core.data_fetcher import DataFetcher

def train_lstm_model(ticker_symbol: str = "AAPL", period: str = "5y",
                     look_back: int = 60, split_ratio: float = 0.8):
    """
    Trains and saves a multivariate LSTM model for stock Open and Close price prediction.
    This script is designed to be run locally, and the generated files must be committed to Git.
    """
    print(f"Starting multivariate LSTM model training for {ticker_symbol}...")

    # 1. Fetch Data
    data_fetcher = DataFetcher()
    df = data_fetcher.fetch_historical_data(ticker_symbol, period=period)
    if df.empty or 'Open' not in df.columns or 'Close' not in df.columns:
        print("Failed to fetch historical data or required columns missing. Aborting training.")
        return

    # Use 'Open' and 'Close' prices for training
    data = df[['Open', 'Close']].values

    # 2. Scale Data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Save the fitted scaler
    model_dir = "data/model"
    os.makedirs(model_dir, exist_ok=True)
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")

    # 3. Create Sequences for LSTM
    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i-look_back:i, :])
        y.append(scaled_data[i, :])
    X, y = np.array(X), np.array(y)

    if X.shape[0] == 0:
        print(f"Not enough data points to create sequences with look_back={look_back}. Aborting training.")
        return

    # Reshape X for LSTM input: (samples, timesteps, features)
    X = X.reshape(X.shape[0], X.shape[1], 2) # 2 features: Open and Close

    # 4. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1-split_ratio, random_state=42, shuffle=False)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")

    # 5. Build LSTM Model
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(look_back, 2)), # Input shape for 2 features
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=2) # Output layer for 2 values (Open, Close)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()

    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint(
        filepath=os.path.join(model_dir, "lstm_model.h5"),
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )

    # 6. Train Model
    model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping, model_checkpoint],
        verbose=1
    )

    print("Model training complete.")
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    print(f"Train Loss: {train_loss:.4f}")
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Trained model saved to {os.path.join(model_dir, 'lstm_model.h5')}")

if __name__ == "__main__":
    train_lstm_model(ticker_symbol="AAPL", period="5y", look_back=60)
