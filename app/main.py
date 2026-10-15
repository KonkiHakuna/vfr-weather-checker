
import asyncio

import httpx
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


async def process_route_point(
    point: dict,
    cruise_altitude_ft: int,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore
):

    # Limit the number of simultaneous weather requests.
    async with semaphore:
        # Fetch forecasts from both providers concurrently.
        open_meteo_weather, met_norway_weather = await asyncio.gather(
            get_weather(
                point["latitude"],
                point["longitude"],
                point["time"],
                cruise_altitude_ft,
                client
            ),
            get_met_weather(
                point["latitude"],
                point["longitude"],
                point["time"],
                client
            )
        )

    # Store the forecasts and their comparison.
    point["weather"] = {
        "open_meteo": open_meteo_weather,
        "met_norway": met_norway_weather
    }

    # Compare forecasts only when both providers returned data.
    if open_meteo_weather is not None and met_norway_weather is not None:
        point["weather_comparison"] = compare_weather(
            open_meteo_weather,
            met_norway_weather
        )
    else:
        point["weather_comparison"] = None

    # Evaluate the available Open-Meteo forecast.
    point["evaluation"] = evaluate_weather(open_meteo_weather)


@app.post("/api/v1/flights/check")
async def check_flight(flight: FlightCheckRequest):
    # Resolve ICAO codes into airport coordinates.
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

    # Generate route points with their expected flight times.
    route_points = generate_route_points(
        departure["lat"],
        departure["lon"],
        arrival["lat"],
        arrival["lon"],
        flight.departure.time,
        flight.arrival.time
    )

    # Reuse HTTP connections and limit concurrent route-point processing.
    semaphore = asyncio.Semaphore(2)

    async with httpx.AsyncClient(timeout=15.0) as client:
        await asyncio.gather(
            *[
                process_route_point(
                    point,
                    flight.cruise_altitude_ft,
                    client,
                    semaphore
                )
                for point in route_points
            ]
        )

    # Run the existing synchronous aviation-weather requests in worker threads.
    departure_metar, departure_taf, arrival_metar, arrival_taf = (
        await asyncio.gather(
            asyncio.to_thread(get_metar, flight.departure.icao),
            asyncio.to_thread(get_taf, flight.departure.icao),
            asyncio.to_thread(get_metar, flight.arrival.icao),
            asyncio.to_thread(get_taf, flight.arrival.icao)
        )
    )

    # Evaluate airport forecasts at the requested flight times.
    departure_evaluation = evaluate_taf(
        departure_taf,
        flight.departure.time
    )

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
        "departure": {
            "icao": flight.departure.icao,
            "metar": departure_metar,
            "taf": departure_taf,
            "evaluation": departure_evaluation
        },
        "arrival": {
            "icao": flight.arrival.icao,
            "metar": arrival_metar,
            "taf": arrival_taf,
            "evaluation": arrival_evaluation
        },
        "route_points": route_points,
        "overall_evaluation": overall_evaluation
    }
