import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import json

class LSTMPredictor:
    def __init__(self):
        with open("static/config.json") as f:
            self.config = json.load(f)
        self.scaler = MinMaxScaler()
    
    def train_model(self, data):
        # ... (training logic same as before)
        model.save("models/lstm_model.h5")
    
    def predict(self, data):
        model = tf.keras.models.load_model("models/lstm_model.h5")
        # ... (prediction logic)
        return predictions

predictor = LSTMPredictor()
