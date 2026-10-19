import os

import requests
from dotenv import load_dotenv

from models import FlightQuery

URL = "https://serpapi.com/search.json"


class SerpApiSource:
    def __init__(self, api_key, currency="GBP"):
        self.api_key = api_key
        self.currency = currency

    def fetch(self, query):
        data = requests.get(URL, timeout=60, params={
            "engine": "google_flights", "type": 2, "currency": self.currency,
            "departure_id": query.origin, "arrival_id": query.dest,
            "outbound_date": query.date, "include_airlines": query.airline,
            "api_key": self.api_key,
        }).json()
        trips = data.get("best_flights", []) + data.get("other_flights", [])
        return min((t["price"] for t in trips if len(t["flights"]) == 1 and "price" in t), default=None)


if __name__ == "__main__":
    load_dotenv()
    source = SerpApiSource(os.environ["SERPAPI_KEY"])
    print(source.fetch(FlightQuery("FR", "STN", "PMI", "2026-11-20")))
