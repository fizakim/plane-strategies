from dataclasses import dataclass
from datetime import timedelta

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class FlightQuery:
    airlines: list
    origins: list
    dests: list
    date: str


@dataclass
class Fare:
    airline: str
    flight_number: str
    origin: str
    dest: str
    dep_time: str
    price: float
    airplane: str = None


@dataclass
class Block:
    name: str
    origins: list
    dests: list

    def __post_init__(self):
        if len(self.origins) > 10 or len(self.dests) > 10:
            raise ValueError(self.name + " has more than 10 airports on one side")
        if set(self.origins) & set(self.dests):
            raise ValueError(self.name + " has an airport on both sides")


@dataclass
class Schedule:
    weekdays: list
    lead_days: list

    def departures(self, today):
        result = []
        for lead in self.lead_days:
            d = today + timedelta(days=lead)
            if DAYS[d.weekday()] in self.weekdays:
                result.append((d, lead))
        return result


@dataclass
class Settings:
    airlines: list
    currency: str
    gl: str
    hl: str
    db_path: str
    reserve: int = 0
    max_errors: int = 3
