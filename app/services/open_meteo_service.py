
from datetime import datetime, timezone

import httpx


BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather(
    latitude: float,
    longitude: float,
    time: datetime,
    cruise_altitude_ft: int,
    client: httpx.AsyncClient
):
    # Convert the requested time to UTC.
    utc_time = time.astimezone(timezone.utc)
    date = utc_time.strftime("%Y-%m-%d")

    # Pressure levels used for cruise altitude weather.
    PRESSURE_LEVELS = [1000, 925, 850, 700, 600, 500]

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
            *[
                f"{variable}_{level}hPa"
                for level in PRESSURE_LEVELS
                for variable in (
                    "wind_speed",
                    "wind_direction",
                    "geopotential_height"
                )
            ],
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

        # Convert cruise altitude from feet to meters.
        cruise_altitude_m = cruise_altitude_ft * 0.3048

        # Find the pressure level closest to the requested altitude.
        levels = []

        for level in PRESSURE_LEVELS:
            height = hourly[f"geopotential_height_{level}hPa"][index]
            wind_speed = hourly[f"wind_speed_{level}hPa"][index]
            wind_direction = hourly[f"wind_direction_{level}hPa"][index]

            if height is None or wind_speed is None:
                continue

            levels.append({
                "pressure_hpa": level,
                "height_m": height,
                "wind_speed_kt": wind_speed,
                "wind_direction_deg": wind_direction
            })

        closest_level = (
            min(
                levels,
                key=lambda item: abs(item["height_m"] - cruise_altitude_m)
            )
            if levels
            else None
        )

        return {
            "time": hourly["time"][index],
            "temperature_c": hourly["temperature_2m"][index],
            "visibility_m": hourly["visibility"][index],
            "cloud_cover": hourly["cloud_cover"][index],
            "precipitation_mm": hourly["precipitation"][index],
            "wind_speed_kt": hourly["wind_speed_10m"][index],
            "wind_direction_deg": hourly["wind_direction_10m"][index],
            "cruise_wind": closest_level,
            "wind_gusts_kt": hourly["wind_gusts_10m"][index],
            "cloud_cover_low": hourly["cloud_cover_low"][index],
            "cloud_cover_mid": hourly["cloud_cover_mid"][index],
            "cloud_cover_high": hourly["cloud_cover_high"][index],
        }

    except (KeyError, ValueError, IndexError, TypeError) as exc:
        print(f"Open-Meteo forecast data unavailable: {exc}")
        return None
