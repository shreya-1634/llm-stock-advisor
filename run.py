# your_project/run.py

import sys
import os

# Get the absolute path to the project's root directory
project_root = os.path.abspath(os.path.dirname(__file__))

# Add the project's root directory to the Python path
if project_root not in sys.path:
    sys.path.append(project_root)

# Now, import and run your main script
from scripts import train_model

if __name__ == "__main__":
    train_model.train_lstm_model()
