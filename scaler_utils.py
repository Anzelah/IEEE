# scaler_utils.py
import joblib
from sklearn.preprocessing import MinMaxScaler
import os

SCALER_PATH = "scalers"
SCALER_FILENAME = os.path.join(SCALER_PATH, "numeric_scaler.joblib")

def fit_and_save_scaler(data, numerical_columns):
    """
    Fit and save a MinMaxScaler for numerical columns
    """
    if not os.path.exists(SCALER_PATH):
        os.makedirs(SCALER_PATH)

    scaler = MinMaxScaler()
    scaler.fit(data[numerical_columns])
    joblib.dump(scaler, SCALER_FILENAME)
    return scaler


def load_scaler():
    """
    Load a saved scaler
    """
    return joblib.load(SCALER_FILENAME)
