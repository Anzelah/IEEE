import os
from dotenv import load_dotenv, dotenv_values
import requests
import json

load_dotenv()

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


def get_rainfall_forecast(lat, lon):
    """
    Fetch rainfall data from Open-Meteo
    Open meteo limits 10, 000 calls per day. By default, it fetches rainfall forecast of seven days from current day.
    """
    # Testing the forecast now according to mmy current location. Need to determine how accurate the 7-day forecast is, and whether its better to use the 3-day forecast instead. 
    # Also, should be once in three days then another call once the three(or 7) elapses.

    url = "https://api.open-meteo.com/v1/forecast"
    payload = { 'latitude': lat, 'longitude': lon, 'daily': 'precipitation_sum', 'timezone': 'Africa/Nairobi' } # data is returned in localtime starting at 00.00 local time

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
    
    data = r.json()

    if "daily" in data and "precipitation_sum" in data["daily"]:
        dates = data["daily"]["time"]
        rainfall = data["daily"]["precipitation_sum"]

        forecast = ['date: {}, rainfall: {}mm' .format(dates[i], rainfall[i]) for i in range(len(dates))]
        return forecast
    else:
        return "No rainfall forecast available."


def analyze_rainfall(forecast):
    """
    Use the pulled rainfall forecast to provide planting near-accurate advice.
    """
    if not forecast:
        return "No rainfall data available. Cannot provide advice."

    total_rain = sum(item["rainfall"] for item in forecast)
    first_3_days_rain = sum(item["rainfall"] for item in forecast[:3])

    # Planting within the first 2-weeks of onset of rains is perfect to take advantage of warm temperatures and nitrogen flux effect.
    # Ensure it has rained atleast 40-100mm before planting. Ensures soil moisture is high. Less than 30mm is too low, and more than 100mm(per week) is too much
    # From 0-10 days, that is planting and emergence, 3-5mm per day minimum 2 is ideal, totalling to around 40-100 mm in first 10 days.
    # Avoid planting if less than 25mm is expected for the first 10 days.
    # Heavy rains are expected over a short period of time as it may waterlodge and prevent germination. Anything over 10mm per day causes waterlogging.
    # For higher yields, maize should receive sufficient rainfall during the first 5 weeks after sowing(and the flowering period).

    if first_3_days_rain >= 10:
        return "✅ Rain is expected soon! This is a **good time to plant** maize."
    elif total_rain < 10:
        return "⚠️ Not enough rain in the coming week. **Hold off planting until rain is expected.**"
    elif total_rain > 50:
        return "⛔ Too much rain is coming, risk of **flooding or waterlogging**. Wait before planting."
    else:
        return "ℹ️ Moderate rain is expected. Plant with caution and monitor rainfall."
    

def main():
    location = input("Enter your County and Sub-county (e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    
    if lat and lon:
        forecast = get_rainfall_forecast(lat, lon)
        print(f"Rainfall forecast for {location}: {forecast}")
    else:
        print("Invalid location. Please try again.")


if __name__ == "__main__":
    main()
