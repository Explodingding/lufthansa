from airline_platform.contracts import SourceContract
from airline_platform.contracts.validation import validate_required_fields
from airline_platform.extractors import build_synthetic_data


def test_synthetic_data_satisfies_source_contracts() -> None:
    data = build_synthetic_data()

    assert validate_required_fields(SourceContract.FLIGHTS, data.flights) == []
    assert validate_required_fields(SourceContract.AIRPORTS, data.airports) == []
    assert validate_required_fields(SourceContract.WEATHER, data.weather) == []
    assert validate_required_fields(SourceContract.PASSENGER_EVENTS, data.passenger_events) == []


def test_synthetic_data_links_passenger_events_to_flights() -> None:
    data = build_synthetic_data()
    flight_ids = {flight["flight_id"] for flight in data.flights}

    event_flight_ids = {event["flight_id"] for event in data.passenger_events}

    assert event_flight_ids.issubset(flight_ids)

