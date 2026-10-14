from datetime import datetime
from math import ceil

from app.utils.geo import (
    calculate_distance,
    interpolate_great_circle,
)


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

    # Great-circle distance defines the total route length.
    route_length = calculate_distance(
        start_lat,
        start_lon,
        end_lat,
        end_lon,
    )

    # Point spacing increases with route length.
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

    # The number of intermediate points keeps segments within the selected spacing.
    points_count = max(
        0,
        ceil(route_length / spacing) - 1
    )

    # Departure and arrival are included with all intermediate route points.
    for i in range(points_count + 2):
        ratio = i / (points_count + 1)

        # Spherical interpolation follows the shortest route over the Earth.
        latitude, longitude = interpolate_great_circle(
            start_lat,
            start_lon,
            end_lat,
            end_lon,
            ratio,
        )

        # Route time progresses proportionally with route distance.
        time = departure_time + total_time * ratio

        points.append({
            "latitude": latitude,
            "longitude": longitude,
            "time": time,
        })

    return points