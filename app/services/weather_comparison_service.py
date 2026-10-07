def compare_weather(open_meteo: dict, met_norway: dict):
    if met_norway is None:
        return {
            "providers_available": 1,
            "comparison_available": False
        }

    return {
        "providers_available": 2,
        "comparison_available": True,
        "temperature_difference_c": round(
            abs(
                open_meteo["temperature_c"]
                - met_norway["temperature_c"]
            ),
            1
        ),
        "wind_speed_difference_kt": round(
            abs(
                open_meteo["wind_speed_kt"]
                - met_norway["wind_speed_kt"]
            ),
            1
        ),
        "cloud_cover_difference": round(
            abs(
                open_meteo["cloud_cover"]
                - met_norway["cloud_cover"]
            ),
            1
        )
    }