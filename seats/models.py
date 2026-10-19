from dataclasses import dataclass


@dataclass(frozen=True)
class FlightQuery:
    airline: str
    origin: str
    dest: str
    date: str
