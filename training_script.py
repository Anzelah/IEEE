import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Paths
DATA_PATH = "data/ofra_dataset.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "fertilizer_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
TARGET_ENCODER_PATH = os.path.join(MODEL_DIR, "target_encoder.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.joblib")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Define columns
categorical_cols = ['texture', 'previous_crop']
numerical_cols = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'organic_carbon']
target_col = 'fertilizer_used'

# Split features and target
X_cat = df[categorical_cols].copy()
X_num = df[numerical_cols].copy()
y = df[target_col].copy()

# Encode categorical features
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X_cat[col] = le.fit_transform(X_cat[col])
    encoders[col] = le

# Normalize numerical features
scaler = StandardScaler()
X_num_scaled = scaler.fit_transform(X_num)

# Encode target
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)

# Combine features
X_combined = np.hstack([X_cat.values, X_num_scaled])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_combined, y_encoded, test_size=0.2, random_state=42)

# Train model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Save model and encoders
joblib.dump(clf, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
joblib.dump(target_encoder, TARGET_ENCODER_PATH)
joblib.dump(encoders, ENCODERS_PATH)

print("✅ Model and encoders trained and saved.")

