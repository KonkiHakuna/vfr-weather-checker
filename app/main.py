from fastapi import FastAPI, HTTPException

from app.schemas.flight import FlightCheckRequest
from app.services.airport_service import get_airport
from app.services.route_service import generate_route_points

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

    return {
        "departure": flight.departure.icao,
        "arrival": flight.arrival.icao,
        "route_points": route_points
    }