import airportsdata


# Load airport information once when the module is imported.
# The dictionary is indexed by ICAO airport codes.
airports = airportsdata.load("ICAO")


def get_airport(icao: str):
    # dict.get() returns None instead of raising an exception
    # when the requested airport does not exist.
    return airports.get(icao)