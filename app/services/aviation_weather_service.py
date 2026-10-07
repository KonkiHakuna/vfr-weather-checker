import httpx

from datetime import datetime, timezone

BASE_URL = "https://aviationweather.gov/api/data"

HEADERS = {
    "User-Agent": "VFR-Weather-Checker"
}


def timestamp_to_iso(timestamp: int):
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()

def get_metar(icao: str):
    response = httpx.get(
        f"{BASE_URL}/metar",
        params={
            "ids": icao,
            "format": "json"
        },
        headers=HEADERS
    )

    response.raise_for_status()

    if response.status_code == 204:
        return None

    data = response.json()

    if not data:
        return None

    metar = data[0]

    return {
        "icao": metar["icaoId"],
        "report_time": metar["reportTime"],
        "temperature_c": metar["temp"],
        "dew_point_c": metar["dewp"],
        "wind_direction_deg": metar["wdir"],
        "wind_speed_kt": metar["wspd"],
        "visibility": metar["visib"],
        "pressure_hpa": metar["altim"],
        "flight_category": metar["fltCat"],
        "cloud_cover": metar["cover"],
        "clouds": metar["clouds"],
        "raw_metar": metar["rawOb"],
    }


def get_taf(icao: str):
    response = httpx.get(
        f"{BASE_URL}/taf",
        params={
            "ids": icao,
            "format": "json"
        },
        headers=HEADERS
    )

    response.raise_for_status()

    if response.status_code == 204:
        return None

    data = response.json()

    if not data:
        return None

    taf = data[0]

    forecasts = []

    for forecast in taf["fcsts"]:
        forecasts.append({
            "from": timestamp_to_iso(forecast["timeFrom"]),
            "to": timestamp_to_iso(forecast["timeTo"]),
            "change": forecast["fcstChange"],
            "wind_direction_deg": forecast["wdir"],
            "wind_speed_kt": forecast["wspd"],
            "wind_gust_kt": forecast["wgst"],
            "visibility": forecast["visib"],
            "weather": forecast["wxString"],
            "clouds": forecast["clouds"],
        })

    return {
        "icao": taf["icaoId"],
        "issue_time": taf["issueTime"],
        "valid_from": timestamp_to_iso(taf["validTimeFrom"]),
        "valid_to": timestamp_to_iso(taf["validTimeTo"]),
        "raw_taf": taf["rawTAF"],
        "forecasts": forecasts,
    }