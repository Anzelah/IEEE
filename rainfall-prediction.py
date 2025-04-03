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

    if "daily" in data and "precipitation_sum" in data["daily"]:
        dates = data["daily"]["time"]
        rainfall = data["daily"]["precipitation_sum"]

        forecast = [{ "date": dates[i], "rainfall_mm": rainfall[i] } for i in range(len(dates))]
        print(forecast)
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

    past_rain = sum(f["rainfall_mm"] for f in forecast[:5])  # Last 5 days total forecast is a list/array of dicts. Len of forecast is 15
    last_3_days_rain = sum(f["rainfall_mm"] for f in forecast[:3])  # Last 3 days total
    first_10_days_rain = sum(forecast[i]["rainfall_mm"] for i in range(5, len(forecast)))  # Next 10 days

    report = f"📅 **Past 5 Days Rainfall:** {past_rain:.1f}mm\n"
    report += f"📅 **Last 3 Days Rainfall:** {last_3_days_rain:.1f}mm\n"
    report += f"🌧 **Next 10 Days Expected:** {first_10_days_rain:.1f}mm\n"

    # 🌱 **Planting Conditions**
    if past_rain < 23:
        report += "\n⚠️ Too little rainfall in the past five days. Soil moisture might be too low. Wait for rains before planting"
    elif past_rain > 80:
        report += "\n⛔ Excessive rainfall in the past five days. Soil is likely waterlogged, and your seeds could rot and fail to germinate. Wait 2-3 dry days for the soil to drain before planting"
    elif first_10_days_rain < 20:
        report += "\n⚠️ Insufficient rainfall is expected in the next 10 days. Planting now may lead to poor germination, weak seedlings, and stunted root development. Consider waiting for more rainfall before planting"
    elif first_10_days_rain > 100:
        report += "\n⛔ Excessive rainfall expected in the next 10 days. This could drown your seeds, lead to poor germination, and wash away nutrients your crops need to thrive. Wait for at least 2-3 days after the rain subsides for the soil to dry out before planting."
    elif past_rain > 80 and first_10_days_rain > 100:
        report += "\n⛔ Both past and forecasted rainfall are excessive. This increases the risk of waterlogging, seed rot, and stunted growth. Wait for 2-3 dry days for the soil to drain before planting."
    elif past_rain > 80 and first_10_days_rain < 20:
        report += "\n⚠️ Excessive past rainfall followed by low expected rainfall can cause waterlogged soil now and drought stress later. Wait for the soil to drain and more rainfall to ensure proper moisture levels."
    else:
        report += "\n✅ **Ideal conditions! You can plant now. Past and forecasted rainfall are favorable for healthy seed germination and growth. Ensure soil is well-prepared and monitor weather for any changes. 🌱"

    return report


    

def main():
    location = input("Enter your County and Sub-county(e.g., Nakuru, Bahati): ")
    lat, lon = get_coordinates(location)
    
    if lat and lon:
        forecast = get_rainfall_forecast(lat, lon)
        advice = analyze_rainfall(forecast)

        print(f"\n🌱 **Planting Advice for {location}:**\n")
        print(advice)
    else:
        print("Invalid location. Please try again.")


if __name__ == "__main__":
    main()
