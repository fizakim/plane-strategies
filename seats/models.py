from dataclasses import dataclass


@dataclass
class FlightQuery:
    airlines: list
    origins: list
    dest: str
    date: str


@dataclass
class Fare:
    airline: str
    flight_number: str
    origin: str
    dest: str
    dep_time: str
    price: float
