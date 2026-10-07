from fastapi import FastAPI

from app.schemas.flight import FlightCheckRequest

app = FastAPI(title="VFR Weather Checker")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/flights/check")
def check_flight(flight: FlightCheckRequest):
    return flight