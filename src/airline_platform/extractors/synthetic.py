"""Deterministic synthetic fallback data for local demos and CI."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

DEFAULT_FLIGHT_COUNT = 720
DEMO_START = datetime(2026, 5, 1, 6, 0, tzinfo=UTC)

AIRPORTS = (
    {
        "airport_code": "GDN",
        "airport_name": "Gdansk Lech Walesa Airport",
        "city": "Gdansk",
        "country": "Poland",
        "timezone": "Europe/Warsaw",
        "latitude_deg": 54.3776,
        "longitude_deg": 18.4662,
    },
    {
        "airport_code": "FRA",
        "airport_name": "Frankfurt Airport",
        "city": "Frankfurt",
        "country": "Germany",
        "timezone": "Europe/Berlin",
        "latitude_deg": 50.0379,
        "longitude_deg": 8.5622,
    },
    {
        "airport_code": "MUC",
        "airport_name": "Munich Airport",
        "city": "Munich",
        "country": "Germany",
        "timezone": "Europe/Berlin",
        "latitude_deg": 48.3538,
        "longitude_deg": 11.7861,
    },
    {
        "airport_code": "WAW",
        "airport_name": "Warsaw Chopin Airport",
        "city": "Warsaw",
        "country": "Poland",
        "timezone": "Europe/Warsaw",
        "latitude_deg": 52.1657,
        "longitude_deg": 20.9671,
    },
    {
        "airport_code": "ZRH",
        "airport_name": "Zurich Airport",
        "city": "Zurich",
        "country": "Switzerland",
        "timezone": "Europe/Zurich",
        "latitude_deg": 47.4582,
        "longitude_deg": 8.5555,
    },
)

ROUTES = (
    ("GDN", "FRA"),
    ("FRA", "GDN"),
    ("GDN", "MUC"),
    ("MUC", "GDN"),
    ("WAW", "FRA"),
    ("ZRH", "MUC"),
)


@dataclass(frozen=True)
class SyntheticAirlineData:
    """Synthetic dataset shaped like Middleware source payloads."""

    flights: list[dict[str, object]]
    airports: list[dict[str, object]]
    weather: list[dict[str, object]]
    passenger_events: list[dict[str, object]]


def build_synthetic_data(flight_count: int = DEFAULT_FLIGHT_COUNT) -> SyntheticAirlineData:
    """Build deterministic airline data for local development."""

    return SyntheticAirlineData(
        flights=_build_flights(flight_count),
        airports=[dict(airport) for airport in AIRPORTS],
        weather=_build_weather(),
        passenger_events=_build_passenger_events(flight_count),
    )


def _build_flights(flight_count: int) -> list[dict[str, object]]:
    flights: list[dict[str, object]] = []
    for index in range(flight_count):
        origin, destination = ROUTES[index % len(ROUTES)]
        scheduled = DEMO_START + timedelta(hours=index * 2)
        delay_minutes = _delay_minutes_for(index)
        status = _status_for(index)
        actual = (
            scheduled if status == "cancelled" else scheduled + timedelta(minutes=delay_minutes)
        )
        flight_number = f"LH{1000 + index % 9000}"
        flight_id = f"{flight_number}-{scheduled:%Y-%m-%d}-{index:04d}"

        flights.append(
            {
                "flight_id": flight_id,
                "flight_number": flight_number,
                "origin_airport": origin,
                "destination_airport": destination,
                "scheduled_departure_utc": _format_utc(scheduled),
                "actual_departure_utc": _format_utc(actual),
                "status": status,
            }
        )

    return flights


def _build_weather() -> list[dict[str, object]]:
    weather: list[dict[str, object]] = []
    for day in range(30):
        observed_at = DEMO_START.replace(hour=6) + timedelta(days=day)
        for airport_index, airport in enumerate(AIRPORTS):
            weather.append(
                {
                    "airport_code": airport["airport_code"],
                    "observed_at_utc": _format_utc(observed_at),
                    "temperature_c": round(9.0 + airport_index * 1.8 + day % 9, 1),
                    "wind_speed_kmh": round(8.0 + (day * 3 + airport_index * 5) % 28, 1),
                    "precipitation_mm": round(((day + airport_index) % 6) * 0.4, 1),
                }
            )

    return weather


def _build_passenger_events(flight_count: int) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for index, flight in enumerate(_build_flights(flight_count)):
        flight_id = str(flight["flight_id"])
        scheduled = _parse_utc(str(flight["scheduled_departure_utc"]))

        if index % 3 == 0:
            events.append(
                _passenger_event(
                    event_id=f"evt-checkin-{index:04d}",
                    flight_id=flight_id,
                    event_type="mobile_check_in",
                    event_timestamp=scheduled - timedelta(hours=14),
                    channel="mobile_app",
                )
            )

        if index % 5 == 0:
            events.append(
                _passenger_event(
                    event_id=f"evt-boarding-{index:04d}",
                    flight_id=flight_id,
                    event_type="boarding_pass_viewed",
                    event_timestamp=scheduled - timedelta(hours=2),
                    channel="web",
                )
            )

        if flight["status"] == "delayed":
            events.append(
                _passenger_event(
                    event_id=f"evt-delay-{index:04d}",
                    flight_id=flight_id,
                    event_type="delay_notification_sent",
                    event_timestamp=scheduled + timedelta(minutes=5),
                    channel="mobile_app",
                )
            )

        if flight["status"] == "cancelled":
            events.append(
                _passenger_event(
                    event_id=f"evt-rebooking-{index:04d}",
                    flight_id=flight_id,
                    event_type="rebooking_offer_viewed",
                    event_timestamp=scheduled + timedelta(minutes=10),
                    channel="email",
                )
            )

    return events


def _passenger_event(
    event_id: str,
    flight_id: str,
    event_type: str,
    event_timestamp: datetime,
    channel: str,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "flight_id": flight_id,
        "event_type": event_type,
        "event_timestamp_utc": _format_utc(event_timestamp),
        "channel": channel,
    }


def _status_for(index: int) -> str:
    if index % 97 == 0:
        return "cancelled"
    if index % 10 in {0, 1}:
        return "delayed"
    return "departed"


def _delay_minutes_for(index: int) -> int:
    if _status_for(index) != "delayed":
        return [0, 4, 7, 9, 12][index % 5]
    return 18 + (index * 7) % 73


def _format_utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
