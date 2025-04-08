# encoder_utils.py

import os
import joblib
from sklearn.preprocessing import LabelEncoder

# Define categories for training
CATEGORY_MAP = {
    "soil_texture": [
        "gritty and falls apart easily",
        "smooth and sticky - forms a ball",
        "soft and holds together loosely",
        "smooth like flour but not sticky"
    ],
    "previous_crop": ["maize", "beans", "wheat", "potatoes", "others"],
    "fertilizer_used": ["DAP", "CAN", "Urea", "Compost"]
}

ENCODER_DIR = "encoders"  # Folder to store .pkl files

def fit_and_save_encoders():
    """Train and save encoders for categorical inputs."""
    if not os.path.exists(ENCODER_DIR):
        os.makedirs(ENCODER_DIR)

    for field, categories in CATEGORY_MAP.items():
        encoder = LabelEncoder()
        encoder.fit(categories)
        joblib.dump(encoder, f"{ENCODER_DIR}/{field}_encoder.pkl")
        print(f"Saved {field} encoder.")

def load_encoders():
    """Load pre-trained encoders from disk and return them in a dict."""
    encoders = {}
    for field in CATEGORY_MAP.keys():
        path = f"{ENCODER_DIR}/{field}_encoder.pkl"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Encoder for {field} not found. Run fit_and_save_encoders() first.")
        encoders[field] = joblib.load(path)
    return encoders

# TO ADD AT THE TOP OF MY PREDICTION MODULE OR MAIN SCRIPT
from encoder_utils import load_encoders

encoders = load_encoders()  # Load trained encoders

# Later in your recommendation code:
encoded_data = [
    encoders["soil_texture"].transform([soil_data["soil_texture"]])[0],
    encoders["previous_crop"].transform([soil_data["previous_crop"]])[0],
    encoders["fertilizer_used"].transform([soil_data["fertilizer_used"]])[0],
    soil_data["previous_yield"],
    soil_data["ph"],
    soil_data["nitrogen"],
    soil_data["phosphorus"],
    soil_data["potassium"],
    soil_data["organic_carbon"],
    soil_data["texture"],
]
