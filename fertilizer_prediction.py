import joblib
import requests
import os
from dotenv import load_dotenv
import json 

load_dotenv()

"""
This script predict fertilizer recommendations based on input from the farmer plus soil data pulled from soilgrids API.
"""
# Load the trained model and the label encoder
#model = joblib.load("fertilizer_recommendation_model.pkl")
#encoder = joblib.load("label_encoder.pkl")

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
        "organic_carbon": data.get("carbon_organic"),  #returns an array of dictionaries
        "nitrogen": data.get("nitrogen_total"),
        "phosphorus": data.get("phosphorous_extractable"),
        "potassium": data.get("potassium_extractable"),
        "ph": data.get("ph"),
        "texture": data.get("texture_class")
    }
    return soil_data

# Function to get farmer input and make predictions
def get_farmer_input():
    # Ask for Farmer's Input
    # Different soil texture: Need to refine more("1. Sandy – Feels gritty and falls apart easily, doesn't hold water well.")
    # "2. Loamy – Feels soft and crumbly, holds together a bit, holds moisture well."
    # "3. Clay – Feels sticky or smooth, holds together tightly, drains slowly."
    # "4. Silty – Feels smooth like flour, holds moisture, but not sticky."
    print('Third')

    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    # Collect  farming-specific inputs to be used to train model as well
    previous_yield = float(input("Enter your previous maize yield (bags per acre): "))
    soil_texture = input("Add a little water to your soil and rub it between your fingers. How does it feel? (e.g. gritty and falls apart easily, smooth and sticky - forms a ball, soft and holds together loosely, smooth like flour but not sticky): ")
    previous_crop = input("Enter the previous crop grown (e.g., maize, beans): ")
    fertilizer_used = input("Enter the type of fertilizer you used (e.g., DAP, CAN, Urea, Compost): ") # combined with yields, you can gauge their effectiveness. If implementing is hard, do it in v2

    # Fetch soil data from SoilGrids API
    soil_data = fetch_soil_data(lat, lon)
    
    if soil_data:
        # Combine farmer inputs with fetched soil data
        soil_data["previous_yield"] = previous_yield
        soil_data["soil_texture"] = soil_texture
        soil_data["previous_crop"] = previous_crop
        soil_data["fertilizer_used"] = fertilizer_used
        
        # Prepare the data for prediction
        prediction_data = [
            soil_data["soil_texture"], 
            soil_data["previous_crop"], 
            soil_data["fertilizer_used"],
            soil_data["previous_yield"],
            soil_data["ph"],
            soil_data["nitrogen"],
            soil_data["phosphorus"],
            soil_data["potassium"],
            soil_data["organic_carbon"],
            soil_data["texture"]
        ]
        
        # Convert categorical data (e.g., soil_color, previous_crop) using LabelEncoder
        encoded_data = []
        for i, value in enumerate(prediction_data[:4]):  # The first 4 values are categorical
            encoded_data.append(encoder.transform([value])[0])  # Transform each categorical value
        
        # Add numeric data (e.g., previous_yield, ph, nitrogen)
        encoded_data.extend(prediction_data[4:])  # Add the rest of the numeric values

        # Predict fertilizer recommendation
        prediction = model.predict([encoded_data])[0]  # Make prediction
        
        # Decode the prediction (convert numeric prediction back to original fertilizer type)
        recommended_fertilizer = encoder.inverse_transform([prediction])[0]
        
        return f"Recommended Fertilizer: {recommended_fertilizer}"
    else:
        print("Could not fetch soil data. Please check your location and try again.")
        return None

# Example of how this function might be called
def main():
    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    
    if lat and lon:
        soil_data = fetch_soil_data(lat, lon)
        #advice = analyze_rainfall(forecast)

        print(f"\n🌱 **Planting Advice for {location}:**\n")
        print(soil_data)
    else:
        print("Invalid location. Please try again.")


if __name__ == "__main__":
    main()
