"""Source data contracts used at the ingestion boundary."""

from dataclasses import dataclass
from enum import StrEnum


class SourceContract(StrEnum):
    """Supported source contracts for raw Middleware-facing inputs."""

    FLIGHTS = "flights"
    AIRPORTS = "airports"
    WEATHER = "weather"
    PASSENGER_EVENTS = "passenger_events"


@dataclass(frozen=True)
class ContractField:
    """A minimal contract field definition for raw payload validation."""

    name: str
    dtype: str
    required: bool = True


CONTRACTS: dict[SourceContract, tuple[ContractField, ...]] = {
    SourceContract.FLIGHTS: (
        ContractField("flight_id", "string"),
        ContractField("flight_number", "string"),
        ContractField("origin_airport", "string"),
        ContractField("destination_airport", "string"),
        ContractField("scheduled_departure_utc", "timestamp"),
        ContractField("actual_departure_utc", "timestamp", required=False),
        ContractField("status", "string"),
    ),
    SourceContract.AIRPORTS: (
        ContractField("airport_code", "string"),
        ContractField("airport_name", "string"),
        ContractField("city", "string"),
        ContractField("country", "string"),
        ContractField("timezone", "string"),
    ),
    SourceContract.WEATHER: (
        ContractField("airport_code", "string"),
        ContractField("observed_at_utc", "timestamp"),
        ContractField("temperature_c", "float"),
        ContractField("wind_speed_kmh", "float"),
        ContractField("precipitation_mm", "float"),
    ),
    SourceContract.PASSENGER_EVENTS: (
        ContractField("event_id", "string"),
        ContractField("flight_id", "string"),
        ContractField("event_type", "string"),
        ContractField("event_timestamp_utc", "timestamp"),
        ContractField("channel", "string"),
    ),
}


def get_contract(source: SourceContract) -> tuple[ContractField, ...]:
    """Return the contract definition for a source."""

    return CONTRACTS[source]


def required_field_names(source: SourceContract) -> set[str]:
    """Return required field names for contract validation."""

    return {field.name for field in get_contract(source) if field.required}

