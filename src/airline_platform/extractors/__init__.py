"""Data extractors for public APIs and synthetic fallback sources."""

from airline_platform.extractors.openmeteo import (
    OPEN_METEO_ARCHIVE_URL,
    fetch_openmeteo_weather_for_airports,
    parse_openmeteo_weather,
)
from airline_platform.extractors.ourairports import (
    DEFAULT_EUROPEAN_AIRPORT_CODES,
    fetch_ourairports_airports,
    parse_ourairports_airports,
)
from airline_platform.extractors.synthetic import SyntheticAirlineData, build_synthetic_data

__all__ = [
    "DEFAULT_EUROPEAN_AIRPORT_CODES",
    "OPEN_METEO_ARCHIVE_URL",
    "SyntheticAirlineData",
    "build_synthetic_data",
    "fetch_openmeteo_weather_for_airports",
    "fetch_ourairports_airports",
    "parse_openmeteo_weather",
    "parse_ourairports_airports",
]
