import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier  # You can change to another model
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from encoder_utils import fit_and_save_encoders
from scaler_utils import fit_and_save_scaler

# Configuration
MODEL_PATH = "models"
MODEL_FILENAME = f"{MODEL_PATH}/fertilizer_model.joblib"
categorical_columns = ['soil_texture', 'previous_crop', 'fertilizer_used']
numerical_columns = ['previous_yield', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'organic_carbon']
target_column = 'recommended_fertilizer'

# Step 1: Load dataset
df = pd.read_csv("training_data.csv")  # Replace with your dataset

# Step 2: Drop rows with missing data
df.dropna(subset=categorical_columns + numerical_columns + [target_column], inplace=True)

# Step 3: Encode categorical inputs
encoders = fit_and_save_encoders(df, categorical_columns)
for col in categorical_columns:
    df[col] = encoders[col].transform(df[col])

# Step 4: Scale numerical inputs
scaler = fit_and_save_scaler(df, numerical_columns)
df[numerical_columns] = scaler.transform(df[numerical_columns])

# Step 5: Encode target label
target_encoder = fit_and_save_encoders(df, [target_column])[target_column]
df[target_column] = target_encoder.transform(df[target_column])

# Step 6: Split into train/test
X = df[categorical_columns + numerical_columns]
y = df[target_column]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 7: Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 8: Evaluate
y_pred = model.predict(X_test)
print("📊 Evaluation:")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

# Step 9: Save model and target encoder
if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)
joblib.dump(model, MODEL_FILENAME)
joblib.dump(target_encoder, f"{MODEL_PATH}/target_encoder.joblib")

print("✅ Model, encoders, and scaler saved.")
