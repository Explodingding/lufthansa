"""Extractor for OurAirports public airport metadata."""

import csv
from collections.abc import Callable, Iterable
from io import StringIO

import requests

OURAIRPORTS_AIRPORTS_CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

DEFAULT_EUROPEAN_AIRPORT_CODES = (
    "GDN",
    "FRA",
    "MUC",
    "ZRH",
    "VIE",
    "BRU",
    "HAM",
    "DUS",
    "BER",
    "CPH",
    "WAW",
    "KRK",
    "AMS",
    "LHR",
    "CDG",
    "MAD",
    "BCN",
    "FCO",
)


def fetch_ourairports_airports(
    airport_codes: Iterable[str] = DEFAULT_EUROPEAN_AIRPORT_CODES,
    url: str = OURAIRPORTS_AIRPORTS_CSV_URL,
    timeout_seconds: float = 30.0,
    http_get: Callable[..., object] = requests.get,
) -> list[dict[str, object]]:
    """Fetch and parse airport metadata from the OurAirports CSV endpoint."""

    response = http_get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return parse_ourairports_airports(response.text, airport_codes)


def parse_ourairports_airports(
    csv_content: str,
    airport_codes: Iterable[str] = DEFAULT_EUROPEAN_AIRPORT_CODES,
) -> list[dict[str, object]]:
    """Parse selected airport metadata from OurAirports CSV content."""

    selected_codes = {airport_code.upper() for airport_code in airport_codes}
    rows = csv.DictReader(StringIO(csv_content))
    airports: list[dict[str, object]] = []

    for row in rows:
        iata_code = row.get("iata_code", "").strip().upper()
        if iata_code not in selected_codes:
            continue

        airports.append(
            {
                "airport_code": iata_code,
                "airport_name": row.get("name", "").strip(),
                "city": row.get("municipality", "").strip(),
                "country": row.get("iso_country", "").strip(),
                "latitude_deg": _to_float(row.get("latitude_deg")),
                "longitude_deg": _to_float(row.get("longitude_deg")),
            }
        )

    return sorted(airports, key=lambda airport: str(airport["airport_code"]))


def _to_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None

    return float(value)
