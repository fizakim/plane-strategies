import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_price(origin, dest, date, airline, currency="GBP"):
    data = requests.get("https://serpapi.com/search.json", timeout=60, params={
        "engine": "google_flights", "type": 2, "currency": currency,
        "departure_id": origin, "arrival_id": dest, "outbound_date": date,
        "include_airlines": airline, "api_key": os.environ["SERPAPI_KEY"],
    }).json()
    trips = data.get("best_flights", []) + data.get("other_flights", [])
    print(trips)
    return min((t["price"] for t in trips if len(t["flights"]) == 1 and "price" in t), default=None)


if __name__ == "__main__":
    print(get_price("STN", "PMI", "2026-11-20", "FR"))
