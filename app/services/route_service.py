from datetime import datetime

from app.cli import calculate_distance


def generate_route_points(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    departure_time: datetime,
    arrival_time: datetime,
):
    points = []

    # Total planned flight duration.
    total_time = arrival_time - departure_time


    route_length = calculate_distance(start_lat,start_lon,end_lat,end_lon)

    # Select point spacing based on route length.
    if route_length < 100:
        spacing = 25
    elif route_length < 500:
        spacing = 50
    elif route_length < 1000:
        spacing = 100
    elif route_length < 3000:
        spacing = 250
    else:
        spacing = 500

    # Calculate the number of intermediate points.
    points_count = max(0, int(route_length // spacing))

    # Include departure and arrival in addition to intermediate route points.
    for i in range(points_count + 2):
        ratio = i / (points_count + 1)

        # Linearly interpolate coordinates between departure and arrival.
        latitude = start_lat + (end_lat - start_lat) * ratio
        longitude = start_lon + (end_lon - start_lon) * ratio

        # Estimate the time at this route point using the same progress ratio.
        time = departure_time + total_time * ratio

        points.append({
            "latitude": latitude,
            "longitude": longitude,
            "time": time
        })

    return points