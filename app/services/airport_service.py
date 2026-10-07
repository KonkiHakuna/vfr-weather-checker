import airportsdata


airports = airportsdata.load("ICAO")


def get_airport(icao: str):
    return airports.get(icao)