from datetime import datetime


def evaluate_weather(weather: dict):
    issues = []

    if weather["visibility_m"] < 5000:
        issues.append("low visibility")

    if weather["wind_speed_kt"] > 20:
        issues.append("high wind")

    if weather["wind_gusts_kt"] > 25:
        issues.append("strong wind gusts")

    if weather["precipitation_mm"] > 0:
        issues.append("precipitation")

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
    if taf is None:
        return{
            "rating": "UNKNOWN",
            "issues": ["TAF unavailable"]
        }

    issues = []

    for forecast in taf["forecasts"]:
        start = datetime.fromisoformat(forecast["from"])
        end = datetime.fromisoformat(forecast["to"])

        if not start <= flight_time < end:
            continue

        gust = forecast.get("wind_gust_kt")
        visibility = forecast.get("visibility")

        if gust is not None and gust > 25:
            issues.append("strong wind gusts in TAF")

        if isinstance(visibility, (int, float)) and visibility < 3.1:
            issues.append("low visibility in TAF")

        for cloud in forecast.get("clouds", []):
            cover = cloud.get("cover")
            base = cloud.get("base")

            if cover in ("BKN", "OVC") and base is not None and base < 1500:
                issues.append("low cloud ceiling in TAF")

            if cloud.get("type") in ("CB", "TCU"):
                issues.append("convective in TAF")

    issues = list(dict.fromkeys(issues))

    return {
        "rating": "CAUTION" if issues else "UNKNOWN",
        "issues": issues
    }

def evaluate_flight(route_points: list, departure_evaluation: dict, arrival_evaluation: dict):
    evaluations = [
        departure_evaluation,
        arrival_evaluation
    ]

    for point in route_points:
        evaluations.append(point["evaluation"])

    issues = []

    for evaluation in evaluations:
        for issue in evaluation["issues"]:
            if issue not in issues:
                issues.append(issue)

    ratings = [evaluation["rating"] for evaluation in evaluations]

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