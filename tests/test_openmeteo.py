from airline_platform.extractors.openmeteo import (
    OPEN_METEO_ARCHIVE_URL,
    fetch_openmeteo_weather_for_airports,
    parse_openmeteo_weather,
)

OPEN_METEO_SAMPLE = {
    "hourly": {
        "time": ["2026-05-06T06:00", "2026-05-06T07:00"],
        "temperature_2m": [12.5, 13.1],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [22.0, 21.4],
    }
}


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def json(self) -> dict[str, object]:
        return self._payload

    def raise_for_status(self) -> None:
        return None


def test_parse_openmeteo_weather_returns_contract_records() -> None:
    weather = parse_openmeteo_weather("GDN", OPEN_METEO_SAMPLE)

    assert weather == [
        {
            "airport_code": "GDN",
            "observed_at_utc": "2026-05-06T06:00:00Z",
            "temperature_c": 12.5,
            "wind_speed_kmh": 22.0,
            "precipitation_mm": 0.2,
        },
        {
            "airport_code": "GDN",
            "observed_at_utc": "2026-05-06T07:00:00Z",
            "temperature_c": 13.1,
            "wind_speed_kmh": 21.4,
            "precipitation_mm": 0.0,
        },
    ]


def test_fetch_openmeteo_weather_for_airports_uses_coordinates_and_dates() -> None:
    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params, timeout))
        return FakeResponse(OPEN_METEO_SAMPLE)

    weather = fetch_openmeteo_weather_for_airports(
        [
            {
                "airport_code": "GDN",
                "latitude_deg": 54.3776,
                "longitude_deg": 18.4662,
            }
        ],
        start_date="2026-05-06",
        end_date="2026-05-06",
        timeout_seconds=5,
        http_get=fake_get,
    )

    assert weather[0]["airport_code"] == "GDN"
    assert calls == [
        (
            OPEN_METEO_ARCHIVE_URL,
            {
                "latitude": 54.3776,
                "longitude": 18.4662,
                "start_date": "2026-05-06",
                "end_date": "2026-05-06",
                "hourly": "temperature_2m,precipitation,wind_speed_10m",
                "timezone": "UTC",
            },
            5,
        )
    ]


def test_fetch_openmeteo_weather_skips_airports_without_coordinates() -> None:
    weather = fetch_openmeteo_weather_for_airports(
        [{"airport_code": "GDN"}],
        start_date="2026-05-06",
        end_date="2026-05-06",
    )

    assert weather == []
