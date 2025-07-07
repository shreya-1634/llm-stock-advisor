from core.data_fetcher import fetch_stock_data
from core.predictor import LSTMPredictor
import os

# Create required directories
os.makedirs("models", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Initialize predictor
predictor = LSTMPredictor()

# Fetch training data (using AAPL as example)
print("Fetching training data...")
training_data = fetch_stock_data("AAPL", "2010-01-01", "2023-01-01")

# Train and save model
print("Training model...")
predictor.train_and_save_model(training_data, "models/lstm_model.h5")
print("Model successfully trained and saved to models/lstm_model.h5")
