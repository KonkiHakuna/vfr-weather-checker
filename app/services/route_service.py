from datetime import datetime


def generate_route_points(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    departure_time: datetime,
    arrival_time: datetime,
    points_count: int = 5
):
    points = []

    total_time = arrival_time - departure_time

    for i in range(points_count + 2):
        ratio = i / (points_count + 1)

        latitude = start_lat + (end_lat - start_lat) * ratio
        longitude = start_lon + (end_lon - start_lon) * ratio
        time = departure_time + total_time * ratio

        points.append({
            "latitude": latitude,
            "longitude": longitude,
            "time": time
        })

    return points