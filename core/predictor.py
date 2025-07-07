import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import plotly.graph_objects as go

def prepare_data(data, n_steps=60):
    """
    Prepare data for LSTM model
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
    
    X, y = [], []
    for i in range(n_steps, len(scaled_data)):
        X.append(scaled_data[i-n_steps:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler

def build_lstm_model(input_shape):
    """
    Build LSTM model for price prediction
    """
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def predict_future_prices(data, days=7):
    """
    Predict future stock prices using LSTM
    """
    # Prepare data
    n_steps = 60
    X, y, scaler = prepare_data(data, n_steps)
    
    # Build and train model
    model = build_lstm_model((X.shape[1], 1))
    early_stopping = EarlyStopping(monitor='loss', patience=5)
    model.fit(X, y, epochs=50, batch_size=32, callbacks=[early_stopping], verbose=0)
    
    # Make predictions
    last_sequence = X[-1]
    predictions = []
    
    for _ in range(days):
        next_pred = model.predict(last_sequence.reshape(1, n_steps, 1))
        predictions.append(next_pred[0, 0])
        last_sequence = np.append(last_sequence[1:], next_pred[0, 0])
    
    # Inverse transform predictions
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    
    # Create future dates
    last_date = data.index[-1]
    future_dates = pd.date_range(start=last_date, periods=days+1)[1:]
    
    # Create DataFrame with predictions
    prediction_df = pd.DataFrame({
        'Date': future_dates,
        'Close': predictions.flatten()
    })
    prediction_df.set_index('Date', inplace=True)
    
    # For visualization, we'll add dummy Open, High, Low values
    prediction_df['Open'] = prediction_df['Close'] * 0.99
    prediction_df['High'] = prediction_df['Close'] * 1.01
    prediction_df['Low'] = prediction_df['Close'] * 0.98
    
    return prediction_df
