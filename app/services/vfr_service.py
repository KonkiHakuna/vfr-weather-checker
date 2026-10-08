from datetime import datetime


def evaluate_weather(weather: dict):
    issues = []

    # Check basic weather conditions that may make a VFR flight less suitable.
    if weather["visibility_m"] < 5000:
        issues.append("low visibility")

    if weather["wind_speed_kt"] > 20:
        issues.append("high wind")

    if weather["wind_gusts_kt"] > 25:
        issues.append("strong wind gusts")

    if weather["precipitation_mm"] > 0:
        issues.append("precipitation")

    # The final rating depends on how many issues were detected.
    if not issues:
        rating = "GOOD"

    elif len(issues) == 1:
        rating = "CAUTION"

    else:
        rating = "POOR"

    return {
        "rating": rating,
        "issues": issues
    }


def evaluate_taf(taf: dict | None, flight_time: datetime):
    # TAF data may be unavailable for some airports.
    if taf is None:
        return{
            "rating": "UNKNOWN",
            "issues": ["TAF unavailable"]
        }

    issues = []

    # ICAO code identifies which airport this TAF belongs to.
    icao = taf["icao"]

    # Find forecast periods that include the planned flight time.
    for forecast in taf["forecasts"]:
        start = datetime.fromisoformat(forecast["from"])
        end = datetime.fromisoformat(forecast["to"])

        if not start <= flight_time < end:
            continue

        gust = forecast.get("wind_gust_kt")
        visibility = forecast.get("visibility")

        if gust is not None and gust > 25:
            issues.append(f"{icao}: strong wind gusts in TAF")

        # Visibility is checked only when the API returned a numeric value.
        if isinstance(visibility, (int, float)) and visibility < 3.1:
            issues.append(f"{icao}: low visibility in TAF")

        # Check each reported cloud layer for low ceilings
        # and convective cloud types.
        for cloud in forecast.get("clouds", []):
            cover = cloud.get("cover")
            base = cloud.get("base")

            if cover in ("BKN", "OVC") and base is not None and base < 1500:
                issues.append(f"{icao}: low cloud ceiling in TAF")

            if cloud.get("type") in ("CB", "TCU"):
                issues.append(f"{icao}: convective in TAF")

    # Remove duplicate issues while preserving their original order.
    issues = list(dict.fromkeys(issues))

    return {
        "rating": "CAUTION" if issues else "UNKNOWN",
        "issues": issues
    }


def evaluate_flight(route_points: list, departure_evaluation: dict, arrival_evaluation: dict):
    # Start with airport evaluations and then include all route points.
    evaluations = [
        departure_evaluation,
        arrival_evaluation
    ]

    for point in route_points:
        evaluations.append(point["evaluation"])

    issues = []

    # Merge issues from all parts of the flight without duplicates.
    for evaluation in evaluations:
        for issue in evaluation["issues"]:
            if issue not in issues:
                issues.append(issue)

    ratings = [evaluation["rating"] for evaluation in evaluations]

    # Use the worst detected rating as the overall flight rating.
    if "POOR" in ratings:
        rating = "POOR"
    elif "CAUTION" in ratings:
        rating = "CAUTION"
    elif "GOOD" in ratings:
        rating = "GOOD"
    else:
        rating = "UNKNOWN"

    return {
        "rating": rating,
        "issues": issues
    }