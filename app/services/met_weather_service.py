
from datetime import datetime, timezone

import httpx


BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

# MET Norway requires applications to identify themselves with a User-Agent.
HEADERS = {
    "User-Agent": "VFR-Weather-Checker/0.1"
}


async def get_met_weather(
    latitude: float,
    longitude: float,
    time: datetime,
    client: httpx.AsyncClient
):
    # Fetch the forecast asynchronously using a shared HTTP client.
    try:
        response = await client.get(
            BASE_URL,
            params={
                "lat": latitude,
                "lon": longitude
            },
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        print(f"MET Norway request failed: {exc}")
        return None

    # Find the forecast closest to the requested UTC time.
    try:
        timeseries = data["properties"]["timeseries"]

        if not timeseries:
            return None

        utc_time = time.astimezone(timezone.utc)

        closest = min(
            timeseries,
            key=lambda item: abs(
                datetime.fromisoformat(
                    item["time"].replace("Z", "+00:00")
                ) - utc_time
            )
        )

        forecast_time = datetime.fromisoformat(
            closest["time"].replace("Z", "+00:00")
        )

        time_difference = abs(forecast_time - utc_time)

        # Reject forecasts more than one hour from the requested time.
        if time_difference.total_seconds() > 3600:
            return None

        details = closest["data"]["instant"]["details"]

        # Next-hour precipitation may be missing.
        precipitation = (
            closest["data"]
            .get("next_1_hours", {})
            .get("details", {})
            .get("precipitation_amount")
        )

        wind_speed = details.get("wind_speed")

        return {
            "time": closest["time"],
            "temperature_c": details.get("air_temperature"),
            "relative_humidity": details.get("relative_humidity"),
            "cloud_cover": details.get("cloud_area_fraction"),
            "wind_speed_kt": (
                round(wind_speed * 1.94384, 1)
                if wind_speed is not None
                else None
            ),
            "wind_direction_deg": details.get("wind_from_direction"),
            "precipitation_mm": precipitation,
        }

    except (KeyError, ValueError, TypeError, IndexError) as exc:
        print(f"MET Norway forecast data unavailable: {exc}")
        return None
