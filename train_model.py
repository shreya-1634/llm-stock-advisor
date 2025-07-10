import os
from core.data_fetcher import fetch_stock_data
from core.predictor import LSTMPredictor
from core.config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    logger.info("🚀 Starting training script...")

    # Create required directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # Initialize predictor
    predictor = LSTMPredictor()

    # Fetch training data
    ticker = "AAPL"
    start_date = "2010-01-01"
    end_date = "2023-01-01"
    
    logger.info(f"📈 Fetching historical stock data for {ticker} from {start_date} to {end_date}")
    training_data = fetch_stock_data(ticker, start_date, end_date)

    # Train and save model
    logger.info("🧠 Training LSTM model...")
    model_path = "models/lstm_model.h5"
    predictor.train_and_save_model(training_data, model_path)

    logger.info(f"✅ Model training completed and saved at {model_path}")

if __name__ == "__main__":
    main()
