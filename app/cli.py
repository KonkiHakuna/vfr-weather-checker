
from datetime import datetime, timezone

import httpx

from app.utils.geo import calculate_distance


def get_time(message):
    # Read the flight time in UTC.
    value = input(f"{message} (YYYY-MM-DD HH:MM UTC): ")
    date = datetime.strptime(value, "%Y-%m-%d %H:%M")
    return date.replace(tzinfo=timezone.utc).isoformat()


def display_factors(factors):
    # Display the risk level of each weather factor.
    if not factors:
        print("  Weather factors unavailable")
        return

    for name, level in factors.items():
        label = name.replace("_", " ").capitalize()
        print(f"  {label}: {level}")


def main():
    print("========== VFR Weather Checker ==========")
    print("Please enter the data below:")

    departure = input("Departure ICAO: ").strip().upper()
    departure_time = get_time("Departure Time")

    arrival = input("Arrival ICAO: ").strip().upper()
    arrival_time = get_time("Arrival Time")

    altitude = int(input("Cruise altitude (ft): "))

    # Build the flight request.
    flight = {
        "departure": {
            "icao": departure,
            "time": departure_time
        },
        "arrival": {
            "icao": arrival,
            "time": arrival_time
        },
        "cruise_altitude_ft": altitude
    }

    print("\nChecking weather...\n")

    try:
        response = httpx.post(
            "http://127.0.0.1:8000/api/v1/flights/check",
            json=flight,
            timeout=120
        )
        response.raise_for_status()

    except httpx.HTTPError as error:
        print(f"Request failed: {error}")
        return

    result = response.json()
    evaluation = result["overall_evaluation"]

    print("========== FLIGHT SUMMARY ==========")
    print(f"Route: {departure} -> {arrival}")
    print(f"Cruise altitude: {altitude} ft")
    print(f"Overall risk: {evaluation['risk_level']}")

    # Display the route risk summary and missing data counts.
    print(f"Route points: {evaluation['evaluated_points']}")
    print(f"Missing weather data: {evaluation['missing_weather_data']}")
    print(f"Unknown flight categories: {evaluation['unknown_flight_categories']}")
    print(f"Unknown airport evaluations: {evaluation['unknown_airport_evaluations']}")

    print("\nRisk summary:")
    for level, count in evaluation["risk_counts"].items():
        print(f"- {level}: {count}")

    print("\nIssues:")

    if evaluation["issues"]:
        for issue in evaluation["issues"]:
            print(f"- {issue}")
    else:
        print("- No issues detected")

    print("\n========== AIRPORT WEATHER ==========")

    for airport_name in ("departure", "arrival"):
        airport = result[airport_name]
        airport_evaluation = airport["evaluation"]

        print(f"\n{airport['icao']}:")
        print(f"  Risk: {airport_evaluation['risk_level']}")
        print(
            f"  Flight category: "
            f"{airport_evaluation.get('flight_category', 'UNKNOWN')}"
        )

        display_factors(airport_evaluation.get("factors", {}))

        for issue in airport_evaluation.get("issues", []):
            print(f"  - {issue}")

    print("\n========== ROUTE POINTS ==========")

    points = result["route_points"]
    total_distance = 0

    for index, point in enumerate(points, start=1):
        if index > 1:
            previous_point = points[index - 2]

            distance = calculate_distance(
                previous_point["latitude"],
                previous_point["longitude"],
                point["latitude"],
                point["longitude"]
            )

            total_distance += distance

        # Calculate route progress.
        progress = (
            (index - 1) / (len(points) - 1) * 100
            if len(points) > 1
            else 100
        )

        point_evaluation = point["evaluation"]

        print(
            f"\nPoint {index} "
            f"({total_distance:.0f} km, {progress:.0f}%): "
            f"{point_evaluation['risk_level']}"
        )

        print(
            f"  Flight category: "
            f"{point_evaluation.get('flight_category', 'UNKNOWN')}"
        )

        display_factors(point_evaluation.get("factors", {}))

        if point_evaluation.get("issues"):
            print("  Issues:")

            for issue in point_evaluation["issues"]:
                print(f"  - {issue}")

        else:
            print("  No issues detected")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
