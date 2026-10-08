# VFR Weather Checker

**VFR Weather Checker** is a Python application that checks weather conditions along a planned **VFR (Visual Flight Rules)** route using **FastAPI** and external weather APIs.

Based on information such as:

- Departure airport (ICAO)
- Arrival airport (ICAO)
- Departure time
- Arrival time
- Planned cruise altitude

The application generates a simplified flight route, retrieves weather forecasts for points along the route and evaluates potential weather-related issues.

## Project Status

The core functionality is **implemented and working**.

The application includes a FastAPI backend and a command-line interface (CLI). Further improvements may include more detailed weather evaluation, automated tests and a graphical interface.

## Features

- Flight input using ICAO airport codes
- Route generation between airports
- Weather forecasts for 7 route points
- Weather data from Open-Meteo and MET Norway
- METAR and TAF reports for departure and arrival airports
- Weather comparison between providers
- Simplified VFR weather evaluation
- Overall flight rating and detected weather issues
- Command-line interface (CLI)
- Distance and route progress for each point

## Technologies

- **Python**
- **FastAPI**
- **Pydantic**
- **HTTPX**
- **Open-Meteo API**
- **MET Norway API**
- **AviationWeather.gov API**
- **Git / GitHub**

## Project Structure

```text
app/
├── main.py                          # FastAPI application
├── cli.py                           # Command-line interface
├── schemas/
│   └── flight.py                    # Flight request validation
└── services/
    ├── airport_service.py           # Airport information
    ├── route_service.py             # Route generation
    ├── open_meteo_service.py        # Open-Meteo forecasts
    ├── met_weather_service.py       # MET Norway forecasts
    ├── aviation_weather_service.py  # METAR and TAF
    ├── weather_comparison_service.py # Weather comparison
    └── vfr_service.py               # Weather evaluation
```

## Running the Application

The application requires **two terminals** running simultaneously.

### Terminal 1 — Backend

Open the first terminal and start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Keep this terminal open while using the application.

### Terminal 2 — Command-Line Interface

Open a second terminal, activate the virtual environment and run:

```bash
python -m app.cli
```

Enter the following flight information:

- Departure airport (ICAO)
- Arrival airport (ICAO)
- Departure time (UTC)
- Arrival time (UTC)
- Planned cruise altitude (ft)

The application will display the overall weather rating, detected issues and weather evaluation for each route point.

**Note:** Keep both terminals running while using the application. No web browser is required.

## Disclaimer

This project is intended for **educational purposes only**.

The weather evaluation uses simplified rules and does not replace official aviation weather information or professional flight planning. A `GOOD` rating does not guarantee safe VFR conditions.