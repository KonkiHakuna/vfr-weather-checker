from fastapi import FastAPI, HTTPException

from app.schemas.flight import FlightCheckRequest
from app.services.airport_service import get_airport
from app.services.route_service import generate_route_points
from app.services.open_meteo_service import get_weather
from app.services.aviation_weather_service import get_metar, get_taf
from app.services.met_weather_service import get_met_weather
from app.services.weather_comparison_service import compare_weather
from app.services.vfr_service import evaluate_weather, evaluate_taf, evaluate_flight

# Main FastAPI application.
app = FastAPI(title="VFR Weather Checker")


@app.get("/health")
def health_check():
    # Simple endpoint used to verify that the API is running.
    return {"status": "ok"}


@app.post("/api/v1/flights/check")
def check_flight(flight: FlightCheckRequest):
    # Resolve ICAO codes into airport data such as coordinates.
    departure = get_airport(flight.departure.icao)
    arrival = get_airport(flight.arrival.icao)

    if departure is None:
        raise HTTPException(
            status_code=404,
            detail=f"Airport {flight.departure.icao} not found"
        )

    if arrival is None:
        raise HTTPException(
            status_code=404,
            detail=f"Airport {flight.arrival.icao} not found"
        )

    # Generate intermediate points between departure and arrival,
    # including the expected time at each point.
    route_points = generate_route_points(
        departure["lat"],
        departure["lon"],
        arrival["lat"],
        arrival["lon"],
        flight.departure.time,
        flight.arrival.time
    )

    # Fetch weather data for every route point from two independent sources.
    for point in route_points:
        point["weather"] = {
            "open_meteo": get_weather(
                point["latitude"],
                point["longitude"],
                point["time"]
            ),
            "met_norway": get_met_weather(
                point["latitude"],
                point["longitude"],
                point["time"]
            )
        }

        # Compare both weather providers to show how closely their forecasts match.
        point["weather_comparison"] = compare_weather(
            point["weather"]["open_meteo"],
            point["weather"]["met_norway"]
        )

        # Evaluate whether the weather at this route point is suitable for VFR.
        point["evaluation"] = evaluate_weather(
            get_weather(
                point["latitude"],
                point["longitude"],
                point["time"]
            )
        )

    # Fetch aviation-specific weather for the departure airport.
    departure_metar = get_metar(flight.departure.icao)
    departure_taf = get_taf(flight.departure.icao)
    departure_evaluation = evaluate_taf(
        departure_taf,
        flight.departure.time
    )

    # Fetch aviation-specific weather for the arrival airport.
    arrival_metar = get_metar(flight.arrival.icao)
    arrival_taf = get_taf(flight.arrival.icao)
    arrival_evaluation = evaluate_taf(
        arrival_taf,
        flight.arrival.time
    )

    # Combine airport and route evaluations into one overall flight rating.
    overall_evaluation = evaluate_flight(
        route_points,
        departure_evaluation,
        arrival_evaluation
    )

    return {
        "departure":{
            "icao": flight.departure.icao,
            "metar": departure_metar,
            "taf": departure_taf,
            "evaluation": departure_evaluation
        },
        "arrival":{
            "icao": flight.arrival.icao,
            "metar": arrival_metar,
            "taf": arrival_taf,
            "evaluation": arrival_evaluation
        },
        "route_points": route_points,
        "overall_evaluation": overall_evaluation
    }