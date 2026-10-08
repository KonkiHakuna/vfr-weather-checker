from datetime import datetime, timezone

import httpx

def get_time(message):
    value = input(f"{message} (YYYY-MM-DD HH:MM UTC): ")
    date = datetime.strptime(value, "%Y-%m-%d %H:%M")
    return date.replace(tzinfo=timezone.utc).isoformat()

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
    for index, point in enumerate(result["route_points"],start=1):
        print(f"Point {index}: {point['evaluation']['rating']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
