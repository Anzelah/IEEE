# encoder_utils.py
import joblib
from sklearn.preprocessing import LabelEncoder
import os

ENCODER_PATH = "encoders"

def fit_and_save_encoders(data, categorical_columns):
    """
    Fit and save label encoders for categorical columns
    """
    if not os.path.exists(ENCODER_PATH):
        os.makedirs(ENCODER_PATH)

    encoders = {}
    for col in categorical_columns:
        encoder = LabelEncoder()
        encoder.fit(data[col])
        joblib.dump(encoder, os.path.join(ENCODER_PATH, f"{col}_encoder.joblib"))
        encoders[col] = encoder
    return encoders


def load_encoders(categorical_columns):
    """
    Load pre-trained encoders
    """
    encoders = {}
    for col in categorical_columns:
        encoders[col] = joblib.load(os.path.join(ENCODER_PATH, f"{col}_encoder.joblib"))
    return encoders
