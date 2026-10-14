
from datetime import datetime


RISK_LEVELS = {
    "LOW": 0,
    "MODERATE": 1,
    "HIGH": 2,
    "SEVERE": 3,
}


def get_risk_level(factors: dict) -> str:
    # Use the highest known risk level.
    known = [
        level for level in factors.values()
        if level in RISK_LEVELS
    ]

    if not known:
        return "UNKNOWN"

    return max(known, key=lambda level: RISK_LEVELS[level])


def get_flight_category(visibility_m=None, ceiling_ft=None):
    # Flight category needs visibility or a measured cloud ceiling.
    if visibility_m is None and ceiling_ft is None:
        return "UNKNOWN"

    visibility_sm = (
        visibility_m / 1609.344
        if visibility_m is not None
        else None
    )

    if (
        (visibility_sm is not None and visibility_sm < 1)
        or (ceiling_ft is not None and ceiling_ft < 500)
    ):
        return "LIFR"

    if (
        (visibility_sm is not None and visibility_sm < 3)
        or (ceiling_ft is not None and ceiling_ft < 1000)
    ):
        return "IFR"

    if (
        (visibility_sm is not None and visibility_sm <= 5)
        or (ceiling_ft is not None and ceiling_ft <= 3000)
    ):
        return "MVFR"

    # Without both measurements, VFR cannot be confirmed.
    if visibility_sm is None or ceiling_ft is None:
        return "UNKNOWN"

    return "VFR"


def evaluate_weather(weather: dict | None):
    if weather is None:
        return {
            "rating": "UNKNOWN",
            "risk_level": "UNKNOWN",
            "flight_category": "UNKNOWN",
            "factors": {},
            "issues": ["Weather data unavailable"],
        }

    factors = {}
    issues = []

    visibility = weather.get("visibility_m")
    wind = weather.get("wind_speed_kt")
    gusts = weather.get("wind_gusts_kt")
    precipitation = weather.get("precipitation_mm")

    # Evaluate visibility.
    if visibility is None:
        factors["visibility"] = "UNKNOWN"
        issues.append("Visibility data unavailable")
    elif visibility < 1609:
        factors["visibility"] = "SEVERE"
        issues.append("Very low visibility")
    elif visibility < 5000:
        factors["visibility"] = "HIGH"
        issues.append("Low visibility")
    elif visibility < 8000:
        factors["visibility"] = "MODERATE"
        issues.append("Reduced visibility")
    else:
        factors["visibility"] = "LOW"

    # Evaluate wind speed.
    if wind is None:
        factors["wind"] = "UNKNOWN"
        issues.append("Wind data unavailable")
    elif wind > 30:
        factors["wind"] = "SEVERE"
        issues.append("Very strong wind")
    elif wind > 20:
        factors["wind"] = "HIGH"
        issues.append("Strong wind")
    elif wind > 12:
        factors["wind"] = "MODERATE"
        issues.append("Moderate wind")
    else:
        factors["wind"] = "LOW"

    # Evaluate wind gusts.
    if gusts is None:
        factors["wind_gusts"] = "UNKNOWN"
        issues.append("Wind gust data unavailable")
    elif gusts > 40:
        factors["wind_gusts"] = "SEVERE"
        issues.append("Very strong wind gusts")
    elif gusts > 25:
        factors["wind_gusts"] = "HIGH"
        issues.append("Strong wind gusts")
    elif gusts > 18:
        factors["wind_gusts"] = "MODERATE"
        issues.append("Moderate wind gusts")
    else:
        factors["wind_gusts"] = "LOW"

    # Evaluate precipitation amount.
    if precipitation is None:
        factors["precipitation"] = "UNKNOWN"
        issues.append("Precipitation data unavailable")
    elif precipitation >= 7.5:
        factors["precipitation"] = "SEVERE"
        issues.append("Very heavy precipitation")
    elif precipitation >= 2.5:
        factors["precipitation"] = "HIGH"
        issues.append("Heavy precipitation")
    elif precipitation > 0:
        factors["precipitation"] = "MODERATE"
        issues.append("Precipitation expected")
    else:
        factors["precipitation"] = "LOW"

    risk_level = get_risk_level(factors)

    return {
        "rating": risk_level,
        "risk_level": risk_level,
        "flight_category": get_flight_category(
            visibility_m=visibility
        ),
        "factors": factors,
        "issues": issues,
    }


def evaluate_taf(taf: dict | None, flight_time: datetime):
    if taf is None:
        return {
            "rating": "UNKNOWN",
            "risk_level": "UNKNOWN",
            "flight_category": "UNKNOWN",
            "factors": {},
            "issues": ["TAF unavailable"],
        }

    icao = taf.get("icao", "Airport")
    matching_forecasts = []

    # Find forecasts covering the planned flight time.
    for forecast in taf.get("forecasts", []):
        start = datetime.fromisoformat(forecast["from"])
        end = datetime.fromisoformat(forecast["to"])

        if start <= flight_time < end:
            matching_forecasts.append(forecast)

    if not matching_forecasts:
        return {
            "rating": "UNKNOWN",
            "risk_level": "UNKNOWN",
            "flight_category": "UNKNOWN",
            "factors": {},
            "issues": [f"{icao}: no TAF forecast for flight time"],
        }

    evaluations = []

    for forecast in matching_forecasts:
        factors = {}
        issues = []

        visibility_sm = forecast.get("visibility")
        gusts = forecast.get("wind_gust_kt")

        # TAF visibility is expected in statute miles.
        visibility_m = (
            visibility_sm * 1609.344
            if isinstance(visibility_sm, (int, float))
            else None
        )

        ceiling_ft = None

        for cloud in forecast.get("clouds", []):
            cover = cloud.get("cover")
            base = cloud.get("base")

            if cover in ("BKN", "OVC", "VV") and base is not None:
                ceiling_ft = (
                    base if ceiling_ft is None
                    else min(ceiling_ft, base)
                )

            if cloud.get("type") in ("CB", "TCU"):
                factors["convection"] = "SEVERE"
                issues.append(f"{icao}: convective clouds")

        category = get_flight_category(visibility_m, ceiling_ft)

        if category == "LIFR":
            factors["flight_conditions"] = "SEVERE"
            issues.append(f"{icao}: LIFR conditions")
        elif category == "IFR":
            factors["flight_conditions"] = "HIGH"
            issues.append(f"{icao}: IFR conditions")
        elif category == "MVFR":
            factors["flight_conditions"] = "MODERATE"
            issues.append(f"{icao}: MVFR conditions")
        elif category == "VFR":
            factors["flight_conditions"] = "LOW"
        else:
            factors["flight_conditions"] = "UNKNOWN"

        if gusts is None:
            factors["wind_gusts"] = "UNKNOWN"
        elif gusts > 40:
            factors["wind_gusts"] = "SEVERE"
            issues.append(f"{icao}: very strong wind gusts")
        elif gusts > 25:
            factors["wind_gusts"] = "HIGH"
            issues.append(f"{icao}: strong wind gusts")
        elif gusts > 18:
            factors["wind_gusts"] = "MODERATE"
            issues.append(f"{icao}: moderate wind gusts")
        else:
            factors["wind_gusts"] = "LOW"

        risk_level = get_risk_level(factors)

        evaluations.append({
            "risk_level": risk_level,
            "flight_category": category,
            "factors": factors,
            "issues": issues,
        })

    # Use the most restrictive forecast category.
    category_order = {
        "UNKNOWN": -1,
        "VFR": 0,
        "MVFR": 1,
        "IFR": 2,
        "LIFR": 3,
    }

    category = max(
        (item["flight_category"] for item in evaluations),
        key=lambda value: category_order[value]
    )

    combined_factors = {}

    for evaluation in evaluations:
        for name, level in evaluation["factors"].items():
            previous = combined_factors.get(name, "UNKNOWN")

            if level in RISK_LEVELS and (
                previous not in RISK_LEVELS
                or RISK_LEVELS[level] > RISK_LEVELS[previous]
            ):
                combined_factors[name] = level
            elif name not in combined_factors:
                combined_factors[name] = level

    risk_level = get_risk_level(combined_factors)

    return {
        "rating": risk_level,
        "risk_level": risk_level,
        "flight_category": category,
        "factors": combined_factors,
        "issues": list(dict.fromkeys(
            issue
            for evaluation in evaluations
            for issue in evaluation["issues"]
        )),
    }


def evaluate_flight(
    route_points: list,
    departure_evaluation: dict,
    arrival_evaluation: dict
):
    # Collect airport and route evaluations.
    route_evaluations = [
        point["evaluation"]
        for point in route_points
    ]

    evaluations = [
        departure_evaluation,
        arrival_evaluation,
        *route_evaluations
    ]

    # Collect unique issues.
    issues = list(dict.fromkeys(
        issue
        for evaluation in evaluations
        for issue in evaluation.get("issues", [])
    ))

    # Count route points by risk level.
    risk_counts = {
        "LOW": 0,
        "MODERATE": 0,
        "HIGH": 0,
        "SEVERE": 0,
        "UNKNOWN": 0
    }

    for evaluation in route_evaluations:
        level = evaluation.get("risk_level", "UNKNOWN")
        risk_counts[level if level in risk_counts else "UNKNOWN"] += 1

    # Find the highest known risk across airports and route.
    known_levels = [
        evaluation.get("risk_level")
        for evaluation in evaluations
        if evaluation.get("risk_level") in RISK_LEVELS
    ]

    risk_level = (
        max(known_levels, key=lambda level: RISK_LEVELS[level])
        if known_levels
        else "UNKNOWN"
    )

    # Count unavailable route weather data.
    missing_weather_data = sum(
        not point.get("weather", {}).get("open_meteo")
        for point in route_points
    )

    # Count route points without a confirmed flight category.
    unknown_flight_categories = sum(
        evaluation.get("flight_category") == "UNKNOWN"
        for evaluation in route_evaluations
    )

    # Count unavailable airport assessments.
    unknown_airport_evaluations = sum(
        evaluation.get("risk_level") == "UNKNOWN"
        for evaluation in (
            departure_evaluation,
            arrival_evaluation
        )
    )

    return {
        "rating": risk_level,
        "risk_level": risk_level,
        "issues": issues,
        "risk_counts": risk_counts,
        "missing_weather_data": missing_weather_data,
        "unknown_flight_categories": unknown_flight_categories,
        "unknown_airport_evaluations": unknown_airport_evaluations,
        "evaluated_points": len(route_points)
    }
