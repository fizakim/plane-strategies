import os
import requests
from dotenv import load_dotenv

from .models import Fare, FlightQuery

URL = "https://serpapi.com/search.json"
ACCOUNT_URL = "https://serpapi.com/account.json"


class SerpApiError(Exception):
    pass


class SerpApiSource:
    def __init__(self, api_key, currency="GBP", gl="uk", hl="en"):
        self.api_key = api_key
        self.currency = currency
        self.gl = gl
        self.hl = hl

    def params(self, query):
        return {
            "engine": "google_flights",
            "type": 2,
            "currency": self.currency,
            "gl": self.gl,
            "hl": self.hl,
            "departure_id": ",".join(query.origins),
            "arrival_id": ",".join(query.dests),
            "outbound_date": query.date,
            "include_airlines": ",".join(query.airlines),
        }

    def get(self, url, params):
        params = dict(params, api_key=self.api_key)
        try:
            return requests.get(url, params=params, timeout=120).json()
        except (requests.RequestException, ValueError) as e:
            raise SerpApiError(type(e).__name__) from None

    def raw(self, query):
        data = self.get(URL, self.params(query))
        data.get("search_parameters", {}).pop("api_key", None)
        return data

    def credits_left(self):
        return self.get(ACCOUNT_URL, {})["total_searches_left"]

    @staticmethod
    def parse(data):
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
                    leg.get("airplane"),
                ))
        return fares

    def fetch(self, query):
        data = self.raw(query)
        if "error" in data:
            raise SerpApiError(data["error"])
        return self.parse(data)


if __name__ == "__main__":
    load_dotenv()
    source = SerpApiSource(os.environ["SERPAPI_KEY"])
    query = FlightQuery(["FR", "U2"], ["STN", "LGW", "LTN"], ["BCN"], "2026-11-20")
    for fare in source.fetch(query):
        print(fare)
