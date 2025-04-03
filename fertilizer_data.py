import requests
import pandas as pd

# Load Rainfall Data from Existing System (Assuming it's stored as a CSV or DB)
# Replace with actual function/method to access stored rainfall data
def get_rainfall_data(county, sub_county):
    # Dummy function to simulate fetching rainfall data from our existing system
    # In real case, fetch from database or API endpoint
    return {
        "last_week_rain": 55,  # mm
        "last_3_days_rain": 25,  # mm
        "forecast_7_days": 80,  # mm (predicted)
    }

# Fetch Soil Data from SoilGrids API
def get_soil_data(lat, lon):
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
    return {
        "nitrogen": data["properties"]["nitrogen"]["mean"] if "nitrogen" in data["properties"] else None,
        "phosphorus": data["properties"]["phosphorus"]["mean"] if "phosphorus" in data["properties"] else None,
        "pH": data["properties"]["phh2o"]["mean"] if "phh2o" in data["properties"] else None,
        "organic_carbon": data["properties"]["ocd"]["mean"] if "ocd" in data["properties"] else None,
    }

# Convert County/Sub-county/Ward to Coordinates (For Soil Data Fetching)
def get_coordinates(county, sub_county):
    # TODO: Implement a lookup for lat/lon based on administrative divisions (Use a geocoding service if needed)
    return (-1.286389, 36.817223)  # Example: Nairobi coordinates

# Main Function to Collect Data
def collect_training_data(county, sub_county):
    lat, lon = get_coordinates(county, sub_county)
    soil_data = get_soil_data(lat, lon)
    rainfall_data = get_rainfall_data(county, sub_county)
    
    if soil_data and rainfall_data:
        return {**soil_data, **rainfall_data, "county": county, "sub_county": sub_county }
    else:
        return None

# Example Usage
farmer_location = { "county": "Uasin Gishu", "sub_county": "Eldoret East" }
data_entry = collect_training_data(**farmer_location)
if data_entry:
    df = pd.DataFrame([data_entry])
    df.to_csv("training_data.csv", mode='a', index=False, header=False)
    print("Data collected and stored successfully.")
else:
    print("Failed to collect data.")
