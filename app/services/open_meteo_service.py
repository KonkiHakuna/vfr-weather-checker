from datetime import datetime

import httpx


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float, time: datetime):
    # Open-Meteo request is limited to the date containing the requested time.
    date = time.strftime("%Y-%m-%d")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "visibility",
            "cloud_cover",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "cloud_cover_low",
            "cloud_cover_mid",
            "cloud_cover_high",
        ],
        "wind_speed_unit": "kn",
        "timezone": "UTC",
        "start_date": date,
        "end_date": date,
    }

    # Request hourly forecast data for the selected location and date.
    response = httpx.get(BASE_URL, params=params)

    # Raise an exception if the API returned an unsuccessful HTTP status.
    response.raise_for_status()

    data = response.json()

    # Forecast values are returned in hourly arrays.
    # Find the array index matching the requested UTC hour.
    hour = time.strftime("%Y-%m-%dT%H:00")
    index = data["hourly"]["time"].index(hour)

    # Extract only the weather values needed by the rest of the application.
    return {
        "time": data["hourly"]["time"][index],
        "temperature_c": data["hourly"]["temperature_2m"][index],
        "visibility_m": data["hourly"]["visibility"][index],
        "cloud_cover": data["hourly"]["cloud_cover"][index],
        "precipitation_mm": data["hourly"]["precipitation"][index],
        "wind_speed_kt": data["hourly"]["wind_speed_10m"][index],
        "wind_direction_deg": data["hourly"]["wind_direction_10m"][index],
        "wind_gusts_kt": data["hourly"]["wind_gusts_10m"][index],
        "cloud_cover_low": data["hourly"]["cloud_cover_low"][index],
        "cloud_cover_mid": data["hourly"]["cloud_cover_mid"][index],
        "cloud_cover_high": data["hourly"]["cloud_cover_high"][index],
    }