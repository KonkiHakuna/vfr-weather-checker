from math import radians, degrees, sin, cos, atan2, sqrt, acos


EARTH_RADIUS_KM = 6371.0


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    # Haversine formula calculates the great-circle distance.
    lat_diff = radians(lat2 - lat1)
    lon_diff = radians(lon2 - lon1)

    a = (
        sin(lat_diff / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(lon_diff / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * atan2(
        sqrt(a),
        sqrt(1 - a)
    )


def interpolate_great_circle(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    ratio: float,
) -> tuple[float, float]:
    # Coordinates are converted to radians for spherical calculations.
    lat1 = radians(start_lat)
    lon1 = radians(start_lon)
    lat2 = radians(end_lat)
    lon2 = radians(end_lon)

    # The central angle represents the distance between both points on a sphere.
    cos_angle = (
        sin(lat1) * sin(lat2)
        + cos(lat1) * cos(lat2) * cos(lon2 - lon1)
    )

    # Clamping prevents floating-point errors outside the acos domain.
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle = acos(cos_angle)

    # Identical coordinates return the original point.
    if angle == 0:
        return start_lat, start_lon

    sin_angle = sin(angle)

    # Spherical interpolation follows the shortest path over the Earth.
    a = sin((1.0 - ratio) * angle) / sin_angle
    b = sin(ratio * angle) / sin_angle

    x = (
        a * cos(lat1) * cos(lon1)
        + b * cos(lat2) * cos(lon2)
    )

    y = (
        a * cos(lat1) * sin(lon1)
        + b * cos(lat2) * sin(lon2)
    )

    z = (
        a * sin(lat1)
        + b * sin(lat2)
    )

    latitude = atan2(z, sqrt(x * x + y * y))
    longitude = atan2(y, x)

    return degrees(latitude), degrees(longitude)