from pathlib import Path

from .models import Block, Schedule, Settings

BLOCKS = [
    Block(
        "A_uk_europe",
        origins=["STN", "LGW", "LTN", "MAN", "BRS", "EDI", "BHX", "LPL", "NCL", "GLA"],
        dests=["ALC", "BCN", "AGP", "MAD", "TFS", "LIS", "MXP", "KRK", "AMS", "GVA"],
    ),
    Block(
        "B_italy_spain_domestic",
        origins=["BGY", "MXP", "VCE", "BLQ", "FCO", "TRN", "PSA", "MAD", "BCN", "SVQ"],
        dests=["CTA", "PMO", "CAG", "NAP", "BRI", "BDS", "PMI", "TFS", "IBZ", "VLC"],
    ),
    Block(
        "C_south_north",
        origins=["BGY", "MXP", "FCO", "NAP", "VCE", "BCN", "MAD", "AGP", "LIS", "OPO"],
        dests=["CDG", "ORY", "BVA", "GVA", "BSL", "BER", "CRL", "KRK", "AMS", "NCE"],
    ),
    Block(
        "D_cee_west",
        origins=["BUD", "OTP", "WAW", "WMI", "KTW", "GDN", "WRO", "SOF", "CLJ", "IAS"],
        dests=["LTN", "STN", "FCO", "BGY", "BCN", "MAD", "DTM", "EIN", "CRL", "NAP"],
    ),
]

SCHEDULE = Schedule(
    weekdays=["Tue", "Fri"],
    lead_days=[7, 14, 21, 35, 56, 84],
)

SETTINGS = Settings(
    airlines=["FR", "U2", "W6", "W9", "W4"],
    currency="GBP",
    gl="uk",
    hl="en",
    db_path=str(Path.home() / "seats_data" / "seats.db"),
)
