import joblib
import requests
import os
from dotenv import load_dotenv
import json 
from sklearn.model_selection import train_test_split
# from encoder_utils import load_encoders

# encoder = load_encoders() 

load_dotenv()

def get_coordinates(location):
    """
    Convert County and Sub-county(will add ward for more precisions) to GPS coordinates using OpenCage API.
    This is because the NASA
    """

    OPENCAGE_API = os.getenv('OPENCAGE_API_KEY')
    print('First')

    url = "https://api.opencagedata.com/geocode/v1/json"
    payload = {'q': location, 'key': OPENCAGE_API, 'countrycode': 'ke'}
    
    try:
        r = requests.get(url, params=payload)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Request failed during processing: {err}")
        return None

    try:    
        data = r.json() # only proceeds to here if the request is succesful thanks to the raise-for-status function. However No content 204 might pass here
    except json.JSONDecodeError:
        print("Empty or invalid JSON in response")
        return None
    
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        return lat, lon
    else:
        return None, None
    

# Function to fetch soil data from SoilGrids API (example)
def fetch_soil_data(lat, lon):
    """
    Fetch existing soil data from soilgrids api. 
    This fetches the nitrogen, soil ph, organic carbon density, and phosphorus content
    """
    ISDA_API = os.getenv('ISDA_API_KEY')
    payload = { 'key': ISDA_API, 'lon': lon, 'lat': lat, 'property': [ 'Carbon, organic', 'Nitrogen, total', 'Phosphorus, extractable', 'Potassium, extractable', 'pH' , 'USDA Texture Class' ], 'depth': 0-20 }

    # Query layers endpoint for first time use, then now to our endpoint. Its: https://api.isda-africa.com/v1/layers?key=mykeynostring
    url = "https://rest.isda-africa.com/soilproperty"

    first_payload = { 'key': ISDA_API }
    first_url = 'https://api.isda-africa.com/v1/layers'
    res = requests.get(first_url, params=first_payload)
    print(res)
    # Only for first API call

    try:
        r = requests.get(url, params=payload, timeout=10)
        print(r.url) # test if url is alright and encoding okay
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("Request failed during processing: {}", format(err))
        return None

    try:
        data = r.json()
        print(data)
    except json.JSONDecodeError:
        print("Empty or invalid JSON in response")
        return None
    
    soil_data = {
        "ph": data.get("ph"),  #returns an array of dictionaries
        "nitrogen": data.get("nitrogen_total"),
        "phosphorus": data.get("phosphorous_extractable"),
        "potassium": data.get("potassium_extractable"),
        "organic_carbon": data.get("carbon_organic"), 
        "texture": data.get("texture_class")
    }
    return soil_data


def clean_and_validate(soil_data):
    """
    Check for missing or invalid soil values in data pulled from the API. 
    Will add defaults later after initial training as it teaches the model to predict accurately
    """
    required_keys = [ 'ph', 'nitrogen', 'phosphorus', 'potassium', 'organic_carbon', 'texture' ]
    for key in required_keys:
        if key not in soil_data or soil_data[key] is None:
            print(f"Missing or invalid data for '{key}', Cannot proceed")
            return None
    return soil_data


def encode_categorical(inputs, encoder):
    """
    Encode all categorical inputs using LabelEncoder
    """
    encoded = []
    for val in inputs:
        try:
            encoded.append(encoder.transform([val])[0])
        except ValueError:
            print(f"Unknown input category: '{val}'. Please use known categories.")
            return None
    return encoded

def normalize_numerical(inputs, scaler):
    """Normalize numerical inputs using fitted scaler"""
    return scaler.transform([inputs])[0].tolist()


# Function to get farmer input and make predictions
def get_farmer_input():
    """Ask for farmer's input to combine with soil data for model training
    """

    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    # Collect  farming-specific inputs to be used to train model as well
    previous_yield = float(input("Enter your previous maize yield (bags per acre): "))
    soil_texture = input("Add a little water to your soil and rub it between your fingers. How does it feel? (e.g. gritty, sticky, soft, smooth): ")
    previous_crop = input("Enter the previous crop grown (e.g., maize, beans): ")
    fertilizer_used = input("Enter the type of fertilizer you used (e.g., DAP, CAN, Urea, Compost): ") # combined with yields, you can gauge their effectiveness. If implementing is hard, do it in v2

    # Fetch soil data from SoilGrids API
    soil_data = fetch_soil_data(lat, lon)

    if soil_data is None:
        print("Could not fetch soil data. Please check your location and try again.")
        return None
    
    soil_data = clean_and_validate(soil_data)
    if soil_data is None:
        return None

    # Combine farmer inputs with fetched soil data
    soil_data.update({
        "previous_yield": previous_yield,
        "soil_texture": soil_texture,
        "previous_crop": previous_crop,
        "fertilizer_used": fertilizer_used
    })
    return soil_data


def recommend_fertilizer():
    """
    Use processed data to predict the best fertilizer
    """
    cleaned_raw_data = get_farmer_input()
    if cleaned_raw_data is None:
        return

    # Prepare input
    categorical = [
        cleaned_raw_data["soil_texture"],
        cleaned_raw_data["previous_crop"],
        cleaned_raw_data["fertilizer_used"]
    ]
    numeric = [
        cleaned_raw_data["previous_yield"],
        cleaned_raw_data["ph"],
        cleaned_raw_data["nitrogen"],
        cleaned_raw_data["phosphorus"],
        cleaned_raw_data["potassium"],
        cleaned_raw_data["organic_carbon"]
    ]

    encoded_cats = encode_categorical(categorical, encoder)
    if encoded_cats is None:
        return
    normalized_nums = normalize_numerical(numeric, scaler)

    # Combine and predict
    final_input = encoded_cats + normalized_nums
    prediction = model.predict([final_input])[0]
    recommendation = encoder.inverse_transform([prediction])[0]

    print(f"🌱 Recommended Fertilizer: {recommendation}")


if __name__ == "__main__":
    recommend_fertilizer()
