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
    Open meteo limits 10, 000 calls per day
    Fetch 7-day rainfall forecast from Open-Meteo API.
    """
    payload = { 'latitude': lat, 'longitude': lon, 'daily': 'precipitation_sum', 'timezone': 'Africa/Nairobi' }
    url = "https://api.open-meteo.com/v1/forecast"

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

        forecast = [{"date": dates[i], "rainfall_mm": rainfall[i]} for i in range(len(dates))]
        return forecast
    else:
        return "No rainfall forecast available."
    

def main():
    location = input("Enter your County and Sub-county (e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    print(lat)
    print(lon)
    
    if lat and lon:
        forecast = get_rainfall_forecast(lat, lon)
        print(f"Rainfall forecast for {location}: {forecast}")
    else:
        print("Invalid location. Please try again.")

if __name__ == "__main__":
    main()
