"""Extractor for Open-Meteo historical weather data."""

from collections.abc import Callable, Iterable, Mapping

import requests

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_HOURLY_VARIABLES = "temperature_2m,precipitation,wind_speed_10m"


def fetch_openmeteo_weather_for_airports(
    airports: Iterable[Mapping[str, object]],
    start_date: str,
    end_date: str,
    max_airports: int = 5,
    url: str = OPEN_METEO_ARCHIVE_URL,
    timeout_seconds: float = 30.0,
    http_get: Callable[..., object] = requests.get,
) -> list[dict[str, object]]:
    """Fetch hourly historical weather for airports with coordinates."""

    weather_records: list[dict[str, object]] = []

    for airport in list(airports)[:max_airports]:
        airport_code = str(airport.get("airport_code", "")).strip().upper()
        latitude = airport.get("latitude_deg")
        longitude = airport.get("longitude_deg")
        if not airport_code or latitude is None or longitude is None:
            continue

        response = http_get(
            url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": OPEN_METEO_HOURLY_VARIABLES,
                "timezone": "UTC",
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        weather_records.extend(parse_openmeteo_weather(airport_code, response.json()))

    return weather_records


def parse_openmeteo_weather(
    airport_code: str,
    payload: Mapping[str, object],
) -> list[dict[str, object]]:
    """Parse Open-Meteo hourly weather payload into source contract records."""

    hourly = payload.get("hourly")
    if not isinstance(hourly, Mapping):
        return []

    timestamps = _as_list(hourly.get("time"))
    temperatures = _as_list(hourly.get("temperature_2m"))
    precipitation = _as_list(hourly.get("precipitation"))
    wind_speeds = _as_list(hourly.get("wind_speed_10m"))

    record_count = min(
        len(timestamps),
        len(temperatures),
        len(precipitation),
        len(wind_speeds),
    )

    return [
        {
            "airport_code": airport_code,
            "observed_at_utc": _to_utc_timestamp(timestamps[index]),
            "temperature_c": temperatures[index],
            "wind_speed_kmh": wind_speeds[index],
            "precipitation_mm": precipitation[index],
        }
        for index in range(record_count)
    ]


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value

    return []


def _to_utc_timestamp(value: object) -> str:
    timestamp = str(value)
    if timestamp.endswith("Z") or timestamp.endswith("+00:00"):
        return timestamp

    return f"{timestamp}:00Z" if len(timestamp) == 16 else f"{timestamp}Z"
