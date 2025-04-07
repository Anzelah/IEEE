import joblib
import requests
import os
from dotenv import load_dotenv 

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
    

# Function to fetch soil data from SoilGrids API (example)
def fetch_soil_data(lat, lon):
    """
    Fetch existing soil data from soilgrids api. 
    This fetches the nitrogen, soil ph, organic carbon density, and phosphorus content
    """
    print('Second')
    payload = { 'lon': lon, 'lat': lat }
    url = "https://rest.isda-africa.com/soil/point"

    try:
        r = requests.get(url, params=payload)
        print(r.url) # test if url is alright and encoding okay
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(err.response.text)
        return None


    print('Reached here')
    data = r.json()
    print(data)
    soil_data = {
        "ph": data.get("ph"),
        "organic_carbon": data.get("organic_carbon"),
        "texture": data.get("texture"),
        "nitrogen": data.get("nitrogen"),
        "phosphorus": data.get("phosphorus"),
        "potassium": data.get("potassium")
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
    print("Please provide the following details:")

    # Collect inputs
    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)

    previous_yield = float(input("Enter your previous maize yield (bags per acre): "))
    soil_color = input("Enter your soil color (e.g., black, brown, red): ")
    soil_texture = input("Add a little water to your soil and rub it between your fingers. How does it feel? (e.g. gritty and falls apart easily, smooth and sticky - forms a ball, soft and holds together loosely, smooth like flour but not sticky): ")
    previous_crop = input("Enter the previous crop grown (e.g., maize, beans): ")
    fertilizer_used = input("Enter the type of fertilizer you used (e.g., DAP, CAN, Urea, Compost): ") # combine dwith yields, you can gauge their effectiveness

    # Fetch soil data from SoilGrids API
    soil_data = fetch_soil_data(lat, lon)
    
    if soil_data:
        # Combine farmer inputs with fetched soil data
        soil_data["previous_yield"] = previous_yield
        soil_data["soil_color"] = soil_color
        soil_data["soil_texture"] = soil_texture
        soil_data["previous_crop"] = previous_crop
        soil_data["fertilizer_used"] = fertilizer_used
        
        # Prepare the data for prediction
        prediction_data = [
            soil_data["soil_color"], 
            soil_data["soil_texture"], 
            soil_data["previous_crop"], 
            soil_data["fertilizer_used"],
            soil_data["previous_yield"],
            soil_data["ph"],
            soil_data["nitrogen"],
            soil_data["phosphorus"],
            soil_data["potassium"],
            soil_data["organic_carbon"]
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
