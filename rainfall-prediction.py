import os
from dotenv import load_dotenv, dotenv_values
from datetime import datetime, timedelta
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

    # Gets the rainfall forecast for the past 5 days, and the next 10 days
    url = "https://api.open-meteo.com/v1/forecast"
    payload = { 'latitude': lat, 'longitude': lon, 'daily': 'precipitation_sum', 'timezone': 'Africa/Nairobi', 'forecast_days': 10, 'past_days': 5 } # data is returned in localtime starting at 00.00 local time

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
    print(data)

    if "daily" in data and "precipitation_sum" in data["daily"]:
        dates = data["daily"]["time"]
        rainfall = data["daily"]["precipitation_sum"]

        forecast = ['date: {}, rainfall_mm: {}' .format(dates[i], rainfall[i]) for i in range(len(dates))]
        return forecast

    return None


def analyze_rainfall(forecast):
    """
    Use the pulled rainfall forecast to provide near-accurate planting advice.
    """
    # Planting within the first 2-weeks of onset of rains is perfect to take advantage of warm temperatures and nitrogen flux effect.
    # Ensure it has rained atleast 40-100mm before planting. Ensures soil moisture is high. Less than 30mm is too low, and more than 100mm(per week) is too much
    # From 0-10 days, that is planting and emergence, 3-5mm per day minimum 2 is ideal, totalling to around 40-100 mm in first 10 days.
    # Avoid planting if less than 25mm is expected for the first 10 days.
    # Heavy rains are expected over a short period of time as it may waterlodge and prevent germination. Anything over 10mm(more than 100mm over the next 10 days) per day causes waterlogging.
    # For higher yields, maize should receive sufficient rainfall during the first 5 weeks after sowing(and the flowering period).
    # Factor in the innacuracy especially from 10-day forecasts. Might do 3-day forecasts (in addition to the 10-day forecasts)

    if not forecast:
        return "No rainfall data available. Cannot provide advice."

    
    past_rain = sum(f["rainfall_mm"] for f in forecast[:5])  # Last 5 days total
    last_3_days_rain = sum(f["rainfall_mm"] for f in forecast[:3])  # Last 3 days total

    first_7_days_rain = sum(forecast[i]["rainfall_mm"] for i in range(7, min(14, len(forecast))))  # Next 7 days
    max_daily_rain = max(forecast[i]["rainfall_mm"] for i in range(7, min(14, len(forecast))))  # Next 7 days

    report = f"📅 **Past 7 Days Rainfall:** {past_rain:.1f}mm\n"
    report += f"📅 **Last 3 Days Rainfall:** {last_3_days_rain:.1f}mm\n"
    report += f"🌧 **Next 7 Days Expected:** {first_7_days_rain:.1f}mm\n"

    # 🌱 **Planting Conditions**
    if first_7_days_rain < 25:
        report += "\n⚠️ Too little rainfall expected (<25mm in 7 days). **Wait before planting.**"
    elif first_7_days_rain > 100:
        report += "\n⛔ Excessive rainfall (>100mm in 7 days). **Risk of waterlogging. Wait before planting.**"
    elif max_daily_rain > 10:
        report += "\n⛔ Heavy rain (>10mm per day). **Risk of waterlogging & poor germination.** Consider waiting."
    elif first_7_days_rain < 40:
        report += "\n⚠️ Initial rainfall too low (<40mm in 7 days). **Wait for more consistent rain.**"
    else:
        report += "\n✅ **Ideal conditions! You can plant now.**"

    return report


    

def main():
    location = input("Enter your County and Sub-county (e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    
    if lat and lon:
        forecast = get_rainfall_forecast(lat, lon)
        #advice = analyze_rainfall(forecast)

        #print(f"\n🌱 **Planting Advice for {location}:**\n")
        #print(advice)
    else:
        print("Invalid location. Please try again.")


if __name__ == "__main__":
    main()
