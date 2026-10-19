import os
import requests
from dotenv import load_dotenv

from .models import Fare, FlightQuery

URL = "https://serpapi.com/search.json"


class SerpApiSource:
    def __init__(self, api_key, currency="GBP"):
        self.api_key = api_key
        self.currency = currency

    def fetch(self, query):
        params = {
            "engine": "google_flights",
            "type": 2,
            "currency": self.currency,
            "departure_id": ",".join(query.origins),
            "arrival_id": query.dest,
            "outbound_date": query.date,
            "include_airlines": ",".join(query.airlines),
            "api_key": self.api_key,
        }
        data = requests.get(URL, params=params).json()

        if "error" in data:
            return []

        fares = []
        for trip in data.get("best_flights", []) + data.get("other_flights", []):
            if len(trip["flights"]) == 1:
                leg = trip["flights"][0]
                fares.append(Fare(
                    leg["flight_number"].split()[0],
                    leg["flight_number"],
                    leg["departure_airport"]["id"],
                    leg["arrival_airport"]["id"],
                    leg["departure_airport"]["time"],
                    trip["price"],
                ))
        return fares


if __name__ == "__main__":
    load_dotenv()
    source = SerpApiSource(os.environ["SERPAPI_KEY"])
    query = FlightQuery(["FR", "U2"], ["STN", "LGW", "LTN"], "BCN", "2026-11-20")
    for fare in source.fetch(query):
        print(fare)
