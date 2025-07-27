# your_project/tests/test_predictor.py

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from sklearn.preprocessing import MinMaxScaler
import os

# Adjust imports based on your exact project structure
from core.predictor import Predictor

# --- Fixtures ---

@pytest.fixture
def dummy_historical_df():
    """Provides a dummy DataFrame resembling historical stock data."""
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = {'Close': np.linspace(100, 150, 100) + np.random.randn(100) * 5}
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def mock_keras_model():
    """Mocks a Keras Sequential model."""
    model = MagicMock()
    # Mock the predict method to return a predictable scaled value
    # For a single prediction of one day, it will return [[scaled_value]]
    model.predict.return_value = np.array([[0.5]]) # Example: predicts scaled value of 0.5
    return model

@pytest.fixture
def mock_min_max_scaler():
    """Mocks a MinMaxScaler instance."""
    scaler = MagicMock(spec=MinMaxScaler)
    # Mock transform to return scaled values and inverse_transform to revert
    # These values should align with your dummy_historical_df and mock_keras_model's output
    scaler.fit_transform.return_value = np.linspace(0, 1, 100).reshape(-1, 1)
    scaler.transform.return_value = np.array([[0.4], [0.5], [0.6]]) # Example scaled input for predict
    scaler.inverse_transform.return_value = np.array([[120.0], [130.0], [140.0]]) # Example inverse transformed output
    return scaler

@pytest.fixture
def predictor_instance(mock_keras_model, mock_min_max_scaler):
    """Provides a Predictor instance with mocked dependencies and cleaned test files."""
    test_model_path = "tests/test_model.h5"
    test_scaler_path = "tests/test_scaler.pkl"

    # Clean up any remnants from previous tests
    if os.path.exists(test_model_path): os.remove(test_model_path)
    if os.path.exists(test_scaler_path): os.remove(test_scaler_path)

    # Patch the paths and the external libraries
    with patch('core.predictor.Predictor.model_path', test_model_path), \
         patch('core.predictor.Predictor.scaler_path', test_scaler_path), \
         patch('tensorflow.keras.models.load_model', return_value=mock_keras_model), \
         patch('sklearn.preprocessing.MinMaxScaler', return_value=mock_min_max_scaler):
        
        # We need to simulate the model file existing for load_model to be called
        # Create a dummy file if needed, as load_model checks os.path.exists
        open(test_model_path, 'a').close() 

        predictor = Predictor()
        # Explicitly set the mocked scaler to the predictor instance
        # if the internal _load_scaler logic doesn't fully capture it.
        # predictor.scaler = mock_min_max_scaler # You might need this depending on mock depth
        
        yield predictor

    # Clean up test files after the test
    if os.path.exists(test_model_path): os.remove(test_model_path)
    if os.path.exists(test_scaler_path): os.remove(test_scaler_path)


# --- Test Cases ---

def test_load_model_success(predictor_instance, mock_keras_model):
    """Test if the model loads successfully."""
    # Ensure the mock model is returned
    assert predictor_instance.model is mock_keras_model
    # Assert load_model was called
    # (Note: the patch on load_model ensures it returns mock_keras_model,
    # so we just check if predictor.model is set)

def test_load_model_not_found(predictor_instance):
    """Test when model file does not exist."""
    # Temporarily remove the dummy file
    if os.path.exists(predictor_instance.model_path):
        os.remove(predictor_instance.model_path)
    
    predictor_instance.model = None # Reset model state
    predictor_instance.load_model()
    assert predictor_instance.model is None

def test_preprocess_data_for_prediction(predictor_instance, dummy_historical_df, mock_min_max_scaler):
    """Test data preprocessing for prediction."""
    # Ensure look_back is less than or equal to dummy data length
    if len(dummy_historical_df) < predictor_instance.look_back:
        pytest.skip(f"Dummy data too short ({len(dummy_historical_df)} for look_back {predictor_instance.look_back})")
    
    # Simulating data for scaling for the last `look_back` days
    expected_scaled_input_shape = (1, predictor_instance.look_back, 1)

    # Mock the return of scaler.transform to provide a predictable input for model.predict
    mock_min_max_scaler.transform.return_value = np.random.rand(predictor_instance.look_back, 1)

    processed_data = predictor_instance.preprocess_data_for_prediction(dummy_historical_df)
    
    assert processed_data is not None
    assert processed_data.shape == expected_scaled_input_shape
    mock_min_max_scaler.transform.assert_called_once() # Verify transform was called

def test_predict_prices_success(predictor_instance, dummy_historical_df, mock_keras_model, mock_min_max_scaler):
    """Test successful price prediction."""
    # Set up mock returns for prediction and inverse transform
    mock_keras_model.predict.return_value = np.array([[0.5], [0.6], [0.7]]) # Predict 3 days
    mock_min_max_scaler.inverse_transform.return_value = np.array([[120.0], [130.0], [140.0]]) # Convert to actual prices

    # Ensure look_back is sufficient
    if len(dummy_historical_df) < predictor_instance.look_back:
        pytest.skip(f"Dummy data too short ({len(dummy_historical_df)} for look_back {predictor_instance.look_back})")

    # Set the scaler on the instance, as it might be loaded/created internally
    predictor_instance.scaler = mock_min_max_scaler
    
    # Patch preprocess_data_for_prediction to return a fixed input
    with patch.object(predictor_instance, 'preprocess_data_for_prediction', return_value=np.random.rand(1, predictor_instance.look_back, 1)):
        predicted_series = predictor_instance.predict_prices(dummy_historical_df, num_predictions=3)
        
        assert not predicted_series.empty
        assert len(predicted_series) == 3
        assert predicted_series.name == 'Predicted Close'
        assert predicted_series.dtype == 'float64'
        assert predicted_series.iloc[0] == 120.0 # Check the inverse transformed value
        mock_keras_model.predict.assert_called() # Should be called multiple times for multi-day prediction
        mock_min_max_scaler.inverse_transform.assert_called_once()


def test_predict_prices_no_model(predictor_instance):
    """Test prediction when model is not loaded."""
    predictor_instance.model = None # Simulate no model loaded
    with patch('core.predictor.Predictor.load_model'): # Ensure load_model is called but no model is returned
        predicted_series = predictor_instance.predict_prices(pd.DataFrame({'Close': [100, 101]}))
        assert predicted_series.empty

def test_predict_prices_not_enough_data(predictor_instance):
    """Test prediction when historical data is too short."""
    short_df = pd.DataFrame({'Close': np.random.rand(predictor_instance.look_back - 1)}, 
                            index=pd.date_range(start='2023-01-01', periods=predictor_instance.look_back - 1))
    
    predicted_series = predictor_instance.predict_prices(short_df)
    assert predicted_series.empty
