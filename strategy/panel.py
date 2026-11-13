from dataclasses import dataclass

import numpy as np
import pandas as pd

from analysis.load import load_fares


@dataclass
class Airline:
    name: str
    codes: list


RYANAIR = Airline("Ryanair", ["FR"])
EASYJET = Airline("easyJet", ["U2"])
AIRLINES = [RYANAIR, EASYJET]

CITY = {
    "STN": "LON", "LGW": "LON", "LTN": "LON",
    "BGY": "MIL", "MXP": "MIL",
    "CDG": "PAR", "ORY": "PAR", "BVA": "PAR",
}


def city(airport):
    return CITY.get(airport, airport)


SEATS = {
    "Boeing 737": 189,
    "Boeing 737MAX 8 Passenger": 197,
    "Airbus A319": 156,
    "Airbus A320": 180,
    "Airbus A321": 230,
    "Airbus A321neo": 235,
}
DEFAULT_SEATS = 180


def load_panel():
    df = pd.DataFrame(load_fares()).rename(columns={"airline": "code"})
    names = {code: a.name for a in AIRLINES for code in a.codes}
    df = df[df["code"].isin(names) & (df["price"] > 0)].copy()
    df["airline"] = df["code"].map(names)
    df["depart_date"] = pd.to_datetime(df["depart_date"])
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df["route"] = df["origin"] + "-" + df["dest"]
    df["city_pair"] = df["origin"].map(city) + "-" + df["dest"].map(city)
    df["flight"] = df["flight_number"] + " " + df["dep_time"]
    df["dow"] = df["depart_date"].dt.dayofweek
    df["seats"] = df["airplane"].map(SEATS).fillna(DEFAULT_SEATS)
    df["ln_p"] = np.log(df["price"])
    return df.reset_index(drop=True)

