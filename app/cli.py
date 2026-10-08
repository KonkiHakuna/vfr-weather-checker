from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2

import httpx

def get_time(message):
    value = input(f"{message} (YYYY-MM-DD HH:MM UTC): ")
    date = datetime.strptime(value, "%Y-%m-%d %H:%M")
    return date.replace(tzinfo=timezone.utc).isoformat()

def calculate_distance(lat1, lng1, lat2, lng2):
    earth_radius = 6371

    lat_diff = radians(lat2 - lat1)
    lng_diff = radians(lng2 - lng1)
    a = (sin(lat_diff/2)**2
         + cos(radians(lat1)) * cos(radians(lat2))
         * sin(lng_diff/2) ** 2
         )
    return 2 * earth_radius * atan2(sqrt(a), sqrt(1 - a))

def main():
    print("========== VFR Weather Checker ==========")
    print("Please enter the data under:")

    departure = input("Departure ICAO: ").strip().upper()
    departure_time = get_time("Departure Time ")

    arrival = input("Arrival ICAO: ").strip().upper()
    arrival_time = get_time("Arrival Time ")

    altitude = int(input("Cruise altitude (ft): "))

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

    print("\n Checking weather... \n")

    try:
        response = httpx.post(
            "http://127.0.0.1:8000/api/v1/flights/check",
            json=flight,
            timeout=60
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        print(error)
        return

    result = response.json()
    evaluation = result["overall_evaluation"]

    print("========== FLIGHT SUMMARY ==========")
    print(f"Route: {departure} -> {arrival}")
    print(f"Overall rating: {evaluation['rating']}")

    print("\nIssues:")
    if evaluation["issues"]:
        for issue in evaluation["issues"]:
            print(f"- {issue}")
    else:
        print("- No issues")

    print("========== ROUTE POINTS ==========")

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
        progress = (index - 1) / (len(points) - 1) * 100

        print(
            f"Point {index} "
            f"({total_distance:.0f} km, {progress:.0f}%): "
            f"{point['evaluation']['rating']}"
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
