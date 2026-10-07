from fastapi import FastAPI, HTTPException

from app.schemas.flight import FlightCheckRequest
from app.services.airport_service import get_airport

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

    return {
        "departure": {
            "icao": flight.departure.icao,
            "latitude": departure["lat"],
            "longitude": departure["lon"]
        },
        "arrival": {
            "icao": flight.arrival.icao,
            "latitude": arrival["lat"],
            "longitude": arrival["lon"]
        }
    }