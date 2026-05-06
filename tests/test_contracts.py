from airline_platform.contracts import (
    CommunicationChannel,
    FlightStatus,
    PassengerEventType,
    SourceContract,
    get_contract,
)
from airline_platform.contracts.schemas import required_field_names
from airline_platform.contracts.validation import validate_contract, validate_required_fields


def test_flight_contract_contains_business_keys() -> None:
    field_names = {field.name for field in get_contract(SourceContract.FLIGHTS)}

    assert {"flight_id", "origin_airport", "destination_airport", "status"}.issubset(field_names)


def test_controlled_values_cover_expected_product_language() -> None:
    assert FlightStatus.DELAYED.value == "delayed"
    assert PassengerEventType.DELAY_NOTIFICATION_SENT.value == "delay_notification_sent"
    assert CommunicationChannel.MOBILE_APP.value == "mobile_app"


def test_required_field_names_exclude_optional_fields() -> None:
    required_fields = required_field_names(SourceContract.FLIGHTS)

    assert "flight_id" in required_fields
    assert "actual_departure_utc" not in required_fields


def test_validate_required_fields_reports_missing_fields() -> None:
    errors = validate_required_fields(
        SourceContract.FLIGHTS,
        [{"flight_id": "LH-001", "status": "departed"}],
    )

    assert errors == [
        (
            "flights[0] missing required field(s): "
            "destination_airport, flight_number, origin_airport, scheduled_departure_utc"
        )
    ]


def test_validate_contract_accepts_valid_flight_record() -> None:
    errors = validate_contract(
        SourceContract.FLIGHTS,
        [
            {
                "flight_id": "LH-001",
                "flight_number": "LH001",
                "origin_airport": "GDN",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "2026-05-06T06:30:00Z",
                "actual_departure_utc": "2026-05-06T06:42:00Z",
                "status": "departed",
            }
        ],
    )

    assert errors == []


def test_validate_contract_reports_invalid_flight_values() -> None:
    errors = validate_contract(
        SourceContract.FLIGHTS,
        [
            {
                "flight_id": "",
                "flight_number": "LH001",
                "origin_airport": "Gdansk",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "not-a-date",
                "status": "boarding",
            }
        ],
    )

    assert errors == [
        "flights[0] required field is empty: flight_id",
        (
            "flights[0] invalid value for status: boarding. "
            "Allowed values: cancelled, delayed, departed, scheduled"
        ),
        "flights[0] invalid UTC timestamp for scheduled_departure_utc: not-a-date",
        "flights[0] invalid IATA airport code for origin_airport",
    ]


def test_validate_contract_reports_invalid_passenger_event_values() -> None:
    errors = validate_contract(
        SourceContract.PASSENGER_EVENTS,
        [
            {
                "event_id": "evt-001",
                "flight_id": "LH-001",
                "event_type": "phone_call",
                "event_timestamp_utc": "2026-05-06T06:36:00Z",
                "channel": "fax",
            }
        ],
    )

    assert errors == [
        (
            "passenger_events[0] invalid value for event_type: phone_call. "
            "Allowed values: boarding_pass_viewed, delay_notification_sent, "
            "mobile_check_in, rebooking_offer_viewed"
        ),
        (
            "passenger_events[0] invalid value for channel: fax. "
            "Allowed values: email, mobile_app, sms, web"
        ),
    ]


def test_validate_contract_reports_invalid_weather_values() -> None:
    errors = validate_contract(
        SourceContract.WEATHER,
        [
            {
                "airport_code": "GDANSK",
                "observed_at_utc": "2026-05-06T06:00:00Z",
                "temperature_c": 120,
                "wind_speed_kmh": -1,
                "precipitation_mm": "heavy",
            }
        ],
    )

    assert errors == [
        "weather[0] invalid IATA airport code for airport_code",
        "weather[0] invalid numeric range for temperature_c: 120",
        "weather[0] invalid numeric range for wind_speed_kmh: -1",
        "weather[0] invalid numeric range for precipitation_mm: heavy",
    ]
