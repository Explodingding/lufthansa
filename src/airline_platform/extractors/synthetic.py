"""Deterministic synthetic fallback data for local demos and CI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticAirlineData:
    """Small synthetic dataset shaped like Middleware source payloads."""

    flights: list[dict[str, object]]
    airports: list[dict[str, object]]
    weather: list[dict[str, object]]
    passenger_events: list[dict[str, object]]


def build_synthetic_data() -> SyntheticAirlineData:
    """Build deterministic airline data for local development."""

    return SyntheticAirlineData(
        flights=[
            {
                "flight_id": "LH-001-2026-05-06",
                "flight_number": "LH001",
                "origin_airport": "GDN",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "2026-05-06T06:30:00Z",
                "actual_departure_utc": "2026-05-06T06:42:00Z",
                "status": "departed",
            },
            {
                "flight_id": "LH-002-2026-05-06",
                "flight_number": "LH002",
                "origin_airport": "FRA",
                "destination_airport": "MUC",
                "scheduled_departure_utc": "2026-05-06T09:15:00Z",
                "actual_departure_utc": "2026-05-06T09:15:00Z",
                "status": "departed",
            },
        ],
        airports=[
            {
                "airport_code": "GDN",
                "airport_name": "Gdansk Lech Walesa Airport",
                "city": "Gdansk",
                "country": "Poland",
                "timezone": "Europe/Warsaw",
            },
            {
                "airport_code": "FRA",
                "airport_name": "Frankfurt Airport",
                "city": "Frankfurt",
                "country": "Germany",
                "timezone": "Europe/Berlin",
            },
            {
                "airport_code": "MUC",
                "airport_name": "Munich Airport",
                "city": "Munich",
                "country": "Germany",
                "timezone": "Europe/Berlin",
            },
        ],
        weather=[
            {
                "airport_code": "GDN",
                "observed_at_utc": "2026-05-06T06:00:00Z",
                "temperature_c": 12.5,
                "wind_speed_kmh": 22.0,
                "precipitation_mm": 0.2,
            },
            {
                "airport_code": "FRA",
                "observed_at_utc": "2026-05-06T09:00:00Z",
                "temperature_c": 16.1,
                "wind_speed_kmh": 11.4,
                "precipitation_mm": 0.0,
            },
        ],
        passenger_events=[
            {
                "event_id": "evt-001",
                "flight_id": "LH-001-2026-05-06",
                "event_type": "mobile_check_in",
                "event_timestamp_utc": "2026-05-05T18:10:00Z",
                "channel": "mobile_app",
            },
            {
                "event_id": "evt-002",
                "flight_id": "LH-001-2026-05-06",
                "event_type": "delay_notification_sent",
                "event_timestamp_utc": "2026-05-06T06:36:00Z",
                "channel": "mobile_app",
            },
        ],
    )
