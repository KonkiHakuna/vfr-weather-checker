from fastapi import FastAPI, HTTPException

from app.schemas.flight import FlightCheckRequest
from app.services.airport_service import get_airport
from app.services.route_service import generate_route_points
from app.services.weather_service import get_weather
from app.services.aviation_weather_service import get_metar, get_taf

app = FastAPI(title="VFR Weather Checker")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/flights/check")
def check_flight(flight: FlightCheckRequest):
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

    route_points = generate_route_points(
        departure["lat"],
        departure["lon"],
        arrival["lat"],
        arrival["lon"],
        flight.departure.time,
        flight.arrival.time
    )

    for point in route_points:
        point["weather"] = get_weather(
            point["latitude"],
            point["longitude"],
            point["time"]
        )

    departure_metar = get_metar(flight.departure.icao)
    departure_taf = get_taf(flight.departure.icao)

    arrival_metar = get_metar(flight.arrival.icao)
    arrival_taf = get_taf(flight.arrival.icao)

    return {
        "departure":{
            "icao": flight.departure.icao,
            "metar": departure_metar,
            "taf": departure_taf
        },
        "arrival":{
            "icao": flight.arrival.icao,
            "metar": arrival_metar,
            "taf": arrival_taf
        },
        "route_points": route_points
    }