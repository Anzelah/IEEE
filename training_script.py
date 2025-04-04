import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

"""
This script handles collecting data, preprocessing it, training the model, and saving the trained model to a file.
"""
# Example data collection - You would replace this with real farmer data.
data = {
    'soil_color': ['black', 'brown', 'red', 'black', 'brown'],
    'water_retention': ['fast', 'slow', 'fast', 'slow', 'fast'],
    'previous_crop': ['maize', 'beans', 'maize', 'beans', 'maize'],
    'fertilizer_used': ['DAP', 'Urea', 'DAP', 'Compost', 'DAP'],
    'previous_yield': [30, 25, 28, 22, 35],
    'ph': [6.5, 6.0, 5.8, 6.2, 6.4],
    'nitrogen': [0.12, 0.08, 0.10, 0.09, 0.11],
    'phosphorus': [12, 15, 10, 13, 14],
    'potassium': [110, 120, 115, 118, 100],
    'organic_carbon': [1.1, 0.9, 1.0, 1.2, 1.3],
    'recommended_fertilizer': ['DAP', 'Urea', 'DAP', 'Compost', 'DAP']  # The target variable
}

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Preprocessing - Encoding categorical variables
encoder = LabelEncoder()
df['soil_color'] = encoder.fit_transform(df['soil_color'])
df['water_retention'] = encoder.fit_transform(df['water_retention'])
df['previous_crop'] = encoder.fit_transform(df['previous_crop'])
df['fertilizer_used'] = encoder.fit_transform(df['fertilizer_used'])
df['recommended_fertilizer'] = encoder.fit_transform(df['recommended_fertilizer'])

# Features and target variable
X = df.drop('recommended_fertilizer', axis=1)
y = df['recommended_fertilizer']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
print(f"Model accuracy: {model.score(X_test, y_test) * 100:.2f}%")

# Save the trained model
joblib.dump(model, 'fertilizer_recommendation_model.pkl')
joblib.dump(encoder, 'label_encoder.pkl')
