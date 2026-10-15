
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

def get_display_mode():
    # Let the user choose how much information to display.
    print("\nSelect display mode:")
    print("1. Normal (basic information)")
    print("2. Detailed (all weather information)")

    while True:
        choice = input("Choose mode (1/2): ").strip()

        if choice == "1":
            return False

        if choice == "2":
            return True

        print("Invalid choice. Please enter 1 or 2.")

def main():
    print("========== VFR Weather Checker ==========")

    verbose = get_display_mode()

    print("\nPlease enter the data below:")

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

    # Display the route risk summary.
    print(f"Route points: {evaluation['evaluated_points']}")

    counts = evaluation["risk_counts"]

    print(
        "Risk summary: "
        + " | ".join(
            f"{level}: {count}"
            for level, count in counts.items()
        )
    )

    if verbose:
        # Display additional data availability details.
        print(f"Missing weather data: {evaluation['missing_weather_data']}")
        print(f"Unknown flight categories: {evaluation['unknown_flight_categories']}")
        print(f"Unknown airport evaluations: {evaluation['unknown_airport_evaluations']}")


    print("\nIssues:")

    if evaluation["issues"]:
        for issue in evaluation["issues"]:
            print(f"- {issue}")
    else:
        print("- No issues detected")

    if verbose:
        # Display detailed airport weather information.
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

        # Read cruise altitude wind data.
        open_meteo = point.get("weather", {}).get("open_meteo") or {}
        cruise_wind = open_meteo.get("cruise_wind")

        print(
            f"\nPoint {index} | "
            f"{total_distance:.0f} km | "
            f"{point_evaluation['risk_level']}"
        )

        if cruise_wind:
            print(
                f"  Cruise wind: {cruise_wind['wind_speed_kt']} kt "
                f"from {cruise_wind['wind_direction_deg']}°"
            )
        else:
            print("  Cruise wind: unavailable")

        if verbose:
            # Display detailed weather information.
            print(f"  Route progress: {progress:.0f}%")
            print(
                f"  Flight category: "
                f"{point_evaluation.get('flight_category', 'UNKNOWN')}"
            )

            if cruise_wind:
                print(
                    f"  Forecast level: {cruise_wind['pressure_hpa']} hPa "
                    f"({cruise_wind['height_m']:.0f} m)"
                )

            display_factors(point_evaluation.get("factors", {}))

        issues = point_evaluation.get("issues", [])

        if issues:
            print("  Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("  No issues detected")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
