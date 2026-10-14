
from datetime import datetime, timezone

import httpx


BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather(
    latitude: float,
    longitude: float,
    time: datetime,
    client: httpx.AsyncClient
):
    # Convert the requested time to UTC.
    utc_time = time.astimezone(timezone.utc)
    date = utc_time.strftime("%Y-%m-%d")

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

    # Fetch the forecast asynchronously using a shared HTTP client.
    try:
        response = await client.get(
            BASE_URL,
            params=params
        )
        response.raise_for_status()
        data = response.json()


    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            print("Open-Meteo rate limit reached (429)")
        else:
            print(f"Open-Meteo HTTP error: {exc}")
        return None

    except (httpx.RequestError, ValueError) as exc:
        print(f"Open-Meteo request failed: {exc}")
        return None

    # Find the forecast matching the requested UTC hour.
    hour = utc_time.strftime("%Y-%m-%dT%H:00")

    try:
        hourly = data["hourly"]
        index = hourly["time"].index(hour)

        return {
            "time": hourly["time"][index],
            "temperature_c": hourly["temperature_2m"][index],
            "visibility_m": hourly["visibility"][index],
            "cloud_cover": hourly["cloud_cover"][index],
            "precipitation_mm": hourly["precipitation"][index],
            "wind_speed_kt": hourly["wind_speed_10m"][index],
            "wind_direction_deg": hourly["wind_direction_10m"][index],
            "wind_gusts_kt": hourly["wind_gusts_10m"][index],
            "cloud_cover_low": hourly["cloud_cover_low"][index],
            "cloud_cover_mid": hourly["cloud_cover_mid"][index],
            "cloud_cover_high": hourly["cloud_cover_high"][index],
        }

    except (KeyError, ValueError, IndexError, TypeError) as exc:
        print(f"Open-Meteo forecast data unavailable: {exc}")
        return None
