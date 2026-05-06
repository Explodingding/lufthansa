from airline_platform.contracts import SourceContract, get_contract
from airline_platform.contracts.schemas import required_field_names
from airline_platform.contracts.validation import validate_required_fields


def test_flight_contract_contains_business_keys() -> None:
    field_names = {field.name for field in get_contract(SourceContract.FLIGHTS)}

    assert {"flight_id", "origin_airport", "destination_airport", "status"}.issubset(field_names)


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

