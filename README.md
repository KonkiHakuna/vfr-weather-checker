# VFR Weather Checker

**VFR Weather Checker** is a Python application for checking weather conditions along a planned **VFR (Visual Flight Rules)** route using **FastAPI** and external aviation/weather data sources.

Based on information such as:

- Departure airport (ICAO)
- Arrival airport (ICAO)
- Departure time
- Arrival time
- Planned cruise altitude

the application generates a simplified flight route, retrieves weather forecasts for points along the route and evaluates potential weather-related risks.

## Project Status

The core functionality is **implemented and working**.

The project currently includes:

- FastAPI backend
- Command-line interface
- Route weather evaluation
- Airport METAR/TAF evaluation
- Cruise-altitude wind data
- Overall route risk summary
- Normal and detailed CLI display modes

Further improvements may include more advanced wind analysis, better cloud ceiling support, automated tests and a graphical interface.

## Features

- Flight input using ICAO airport codes
- Validation of departure and arrival times
- Planned cruise altitude input
- Route generation between airports
- Weather forecasts for multiple route points
- Weather data from Open-Meteo
- Weather data from MET Norway
- METAR and TAF reports for departure and arrival airports
- Weather comparison between providers
- Surface wind evaluation
- Wind gust evaluation
- Visibility evaluation
- Precipitation evaluation
- Cruise-altitude wind forecast
- Cruise-altitude wind risk evaluation
- Simplified VFR flight category evaluation
- Overall flight risk level
- Detected weather issues
- Missing weather data handling
- Command-line interface
- Normal and detailed CLI display modes
- Distance and route progress for each route point

## Weather Evaluation

The application evaluates several weather-related factors:

- Visibility
- Surface wind
- Wind gusts
- Precipitation
- Wind at cruise altitude

Each factor is assigned one of the following risk levels:

- `LOW`
- `MODERATE`
- `HIGH`
- `SEVERE`
- `UNKNOWN`

The overall flight risk is based on the highest known risk level detected along the route and at the departure and arrival airports.

### Flight Categories

The application can also estimate simplified flight categories:

- `VFR`
- `MVFR`
- `IFR`
- `LIFR`
- `UNKNOWN`

For route points, the category may be based on visibility only when cloud ceiling data is unavailable.

For airport TAF data, both visibility and available cloud ceiling information are used.

## Cruise Altitude Weather

The selected cruise altitude is used to retrieve wind forecasts from pressure levels available in Open-Meteo.

The application selects the pressure level whose geopotential height is closest to the requested cruise altitude.

Because pressure-level forecasts do not always match the exact requested altitude, cruise wind values should be treated as an approximation.

## Technologies

- **Python**
- **FastAPI**
- **Pydantic**
- **HTTPX**
- **asyncio**
- **Open-Meteo API**
- **MET Norway API**
- **AviationWeather.gov API**
- **Git / GitHub**

## Project Structure

```text
app/
├── main.py                           # FastAPI application
├── cli.py                            # Command-line interface
├── schemas/
│   └── flight.py                     # Flight request validation
├── services/
│   ├── airport_service.py            # Airport information
│   ├── route_service.py              # Route generation
│   ├── open_meteo_service.py         # Open-Meteo forecasts
│   ├── met_weather_service.py        # MET Norway forecasts
│   ├── aviation_weather_service.py   # METAR and TAF
│   ├── weather_comparison_service.py # Weather comparison
│   └── vfr_service.py                # Weather evaluation
└── utils/
    └── geo.py                        # Geographic calculations
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

The CLI will first ask which display mode should be used:

```text
1. Normal
2. Detailed
   ```
   
   Then enter the flight information:
   
   - Departure airport (ICAO)
   - Departure time (UTC)
   - Arrival airport (ICAO)
   - Arrival time (UTC)
   - Planned cruise altitude (ft)
   
   ## CLI Modes
   
   ### Normal Mode

Normal mode displays the most important flight information, including:

- Route
- Cruise altitude
- Overall risk
- Risk summary
- Detected issues
- Route points
- Cruise-altitude wind

### Detailed Mode

Detailed mode includes additional information such as:

- Airport weather evaluation
- Flight category
- Route progress
- Forecast pressure level
- Forecast height
- Individual weather risk factors
- Missing weather information
  

  Actual results depend on the selected route, time, altitude and weather data availability.
  
  ## API Endpoint
  
  The main flight-check endpoint is:
  
  ```text
  POST /api/v1/flights/check
  ```
  
### Request Body
  
  ```json
{
  "departure": {
    "icao": "ICAO_CODE",
    "time": "ISO_8601_DATETIME"
  },
  "arrival": {
    "icao": "ICAO_CODE",
    "time": "ISO_8601_DATETIME"
  },
  "cruise_altitude_ft": "INTEGER"
}
```
  
  ## Limitations
  
  The application uses simplified weather evaluation rules.
  
  Some important limitations include:
  
  - Cruise-altitude wind is based on the nearest available pressure level
  - Cloud ceiling data is not available for every route forecast point
  - Route flight categories may sometimes be based on visibility only
  - Weather providers may temporarily return incomplete or unavailable data
  - Risk thresholds are project-specific and simplified
  - The application does not include aircraft-specific performance limitations
  - Wind direction relative to aircraft heading is not yet evaluated
  
  ## Planned Improvements
  
  Possible future improvements include:
  
  - Headwind and tailwind calculation
  - Crosswind calculation
  - Better cloud ceiling support
  - More advanced flight-category evaluation
  - Temperature at cruise altitude
  - Freezing-level information
  - Improved weather provider comparison
  - Automated tests
  - Graphical user interface
  - Exportable flight weather reports
  
  ## Disclaimer
  
  This project is intended for **educational purposes only**.
  
  The weather evaluation uses simplified rules and does not replace:
  
  - Official aviation weather sources
  - METAR and TAF interpretation by a pilot
  - NOTAM checks
  - Professional flight planning
  - Aircraft-specific operating limitations
  - Pilot judgment
  
  A `LOW` risk level does **not** guarantee safe VFR conditions.
  
  Always use official aviation weather information and appropriate flight-planning procedures before conducting a flight.