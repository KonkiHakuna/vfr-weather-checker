from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class AirportTime(BaseModel):
    # ICAO codes always contain exactly four characters.
    icao: str = Field(min_length=4, max_length=4)
    time: datetime

    @field_validator("icao")
    @classmethod
    def normalize_icao(cls, value: str):
        # Normalize user input so airport lookups are case-independent.
        return value.upper()


class FlightCheckRequest(BaseModel):
    departure: AirportTime
    arrival: AirportTime

    # Cruise altitude must be a positive value.
    cruise_altitude_ft: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_times(self):
        # Validate values that depend on more than one model field.
        if self.arrival.time <= self.departure.time:
            raise ValueError("Arrival time must be later than departure time")

        return self