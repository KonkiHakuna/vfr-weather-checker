from datetime import datetime

import httpx


BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

HEADERS = {
    "User-Agent": "VFR-Weather-Checker/0.1"
}


def get_met_weather(latitude: float, longitude: float, time: datetime):
    response = httpx.get(
        BASE_URL,
        params={
            "lat": latitude,
            "lon": longitude
        },
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()
    timeseries = data["properties"]["timeseries"]

    closest = min(
        timeseries,
        key=lambda item: abs(
            datetime.fromisoformat(
                item["time"].replace("Z", "+00:00")
            ) - time
        )
    )

    forecast_time = datetime.fromisoformat(
        closest["time"].replace("Z", "+00:00")
    )

    time_difference = abs(forecast_time - time)

    if time_difference.total_seconds() > 3600:
        return None

    details = closest["data"]["instant"]["details"]

    precipitation = (
        closest["data"]
        .get("next_1_hours", {})
        .get("details", {})
        .get("precipitation_amount")
    )

    return {
        "time": closest["time"],
        "temperature_c": details.get("air_temperature"),
        "relative_humidity": details.get("relative_humidity"),
        "cloud_cover": details.get("cloud_area_fraction"),
        "wind_speed_kt": round(
            details.get("wind_speed", 0) * 1.94384,
            1
        ),
        "wind_direction_deg": details.get("wind_from_direction"),
        "precipitation_mm": precipitation,
    }