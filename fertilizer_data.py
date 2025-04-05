import requests
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


# Fetch Soil Data from SoilGrids API
def fetch_soil_data(lat, lon):
    """
    Fetch existing soil data from soilgrids api. 
    This fetches the nitrogen, soil ph, organic carbon density, and phosphorus content
    """
    payload = { 'lon': lon, 'lat': lat, 'property': 'nitrogen,phh2o,ocd,phosphorus' }
    url = "https://rest.isric.org/soilgrids/v2.0/properties"

    try:
        r = requests.get(url, params=payload)
        print(r.url) # test if url is alright and encoding okay
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e.response.text)
    except requests.exceptions.ConnectionError as er:
        print(er.response.text)
    except requests.exceptions.Timeout as eg:
        print(eg.response.text)
    except requests.exceptions.RequestException as err:
        print(err.response.text)


    data = r.json()
    soil_data = {
        "nitrogen": data["properties"]["nitrogen"]["mean"] if "nitrogen" in data["properties"] else None,
        "phosphorus": data["properties"]["phosphorus"]["mean"] if "phosphorus" in data["properties"] else None,
        "pH": data["properties"]["phh2o"]["mean"] if "phh2o" in data["properties"] else None,
        "potassium": data["properties"]["potassium"]["mean"] if "potassium" in data["properties"] else None,
        "organic_carbon": data["properties"]["ocd"]["mean"] if "ocd" in data["properties"] else None,
    }
    return soil_data

# Sample Dataset with Previous Yield
data = pd.DataFrame({
    "soil_color": ["black", "brown", "red", "gray", "black"],
    "soil_texture": ["coarse", "soft", "soft", "coarse", "soft"],
    "previous_crop": ["maize", "beans", "maize", "sorghum", "maize"],
    "fertilizer_used": ["DAP", "None", "Urea", "Manure", "CAN"],
    "previous_yield": [18, 12, 15, 20, 10],  # Bags per acre
    "ph": [5.5, 6.2, 5.8, 7.0, 5.4],
    "nitrogen": [0.12, 0.08, 0.14, 0.09, 0.11],
    "phosphorus": [10, 12, 8, 15, 9],
    "potassium": [200, 180, 220, 160, 190],
    "organic_carbon": [1.2, 0.9, 1.4, 0.8, 1.1],  # Organic Carbon %
    "recommended_fertilizer": ["NPK", "Compost", "DAP", "CAN", "Urea"],
})

# Convert Categorical Data to Numbers
encoder = LabelEncoder()
categorical_cols = ["soil_color", "soil_texture", "previous_crop", "fertilizer_used"]
for col in categorical_cols:
    data[col] = encoder.fit_transform(data[col])

# Train-Test Split
X = data.drop(columns=["recommended_fertilizer"])  # Input features
y = data["recommended_fertilizer"]  # Output labels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save Model
joblib.dump(model, "fertilizer_recommendation_model.pkl")
print("Model training complete. Saved as 'fertilizer_recommendation_model.pkl'")

def get_coordinates(location):
    """
    Convert County and Sub-county(will add ward for more precisions) to GPS coordinates using OpenCage API.
    This is because the NASA
    """

    OPENCAGE_API = os.getenv('OPENCAGE_API_KEY')

    url = "https://api.opencagedata.com/geocode/v1/json"
    payload = {'q': location, 'key': OPENCAGE_API, 'countrycode': 'ke'}
    
    try:
        r = requests.get(url, params=payload)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e.response.text)
    except requests.exceptions.ConnectionError as er:
        print(er.response.text)
    except requests.exceptions.Timeout as eg:
        print(eg.response.text)
    except requests.exceptions.RequestException as err:
        print(err.response.text)
        
    data = r.json() # only proceeds to here if the request is succesful thanks to the raise-for-status function
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        return lat, lon
    else:
        return None, None


# Function for Farmer Input
def get_farmer_input():
    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)

    previous_yield = float(input("Enter your previous maize yield (bags per acre): "))  
    soil_color = input("Enter your soil color (e.g., black, brown, red): ")
    soil_texture = input("Enter your soil's texture (e.g. coarse, soft): ")
    previous_crop = input("Enter the previous crop grown (e.g., maize, beans): ")
    fertilizer_used = input("Enter the type of fertilizer you used (e.g., DAP, CAN, Urea, Compost): ")
    
    # Fetch soil data from SoilGrids API
    soil_data = fetch_soil_data(lat, lon)
    
    if soil_data:
        # Combine farmer inputs with fetched soil data
        soil_data["previous_yield"] = previous_yield
        soil_data["soil_color"] = soil_color
        soil_data["soil_texture"] = soil_texture
        soil_data["previous_crop"] = previous_crop
        soil_data["fertilizer_used"] = fertilizer_used

        return soil_data
    else:
        print("Could not fetch soil data. Please check your location and try again.")
        return None