"""Source data contracts used at the ingestion boundary."""

from dataclasses import dataclass
from enum import StrEnum


class SourceContract(StrEnum):
    """Supported source contracts for raw Middleware-facing inputs."""

    FLIGHTS = "flights"
    AIRPORTS = "airports"
    WEATHER = "weather"
    PASSENGER_EVENTS = "passenger_events"


class FlightStatus(StrEnum):
    """Controlled flight statuses accepted at the ingestion boundary."""

    SCHEDULED = "scheduled"
    DEPARTED = "departed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class PassengerEventType(StrEnum):
    """Controlled passenger event types for digital journey analytics."""

    MOBILE_CHECK_IN = "mobile_check_in"
    DELAY_NOTIFICATION_SENT = "delay_notification_sent"
    BOARDING_PASS_VIEWED = "boarding_pass_viewed"
    REBOOKING_OFFER_VIEWED = "rebooking_offer_viewed"


class CommunicationChannel(StrEnum):
    """Controlled channels for passenger communication events."""

    MOBILE_APP = "mobile_app"
    WEB = "web"
    EMAIL = "email"
    SMS = "sms"


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
        ContractField("timezone", "string", required=False),
        ContractField("latitude_deg", "float", required=False),
        ContractField("longitude_deg", "float", required=False),
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

ALLOWED_VALUES: dict[SourceContract, dict[str, set[str]]] = {
    SourceContract.FLIGHTS: {
        "status": {status.value for status in FlightStatus},
    },
    SourceContract.PASSENGER_EVENTS: {
        "event_type": {event_type.value for event_type in PassengerEventType},
        "channel": {channel.value for channel in CommunicationChannel},
    },
}


def get_contract(source: SourceContract) -> tuple[ContractField, ...]:
    """Return the contract definition for a source."""

    return CONTRACTS[source]


def required_field_names(source: SourceContract) -> set[str]:
    """Return required field names for contract validation."""

    return {field.name for field in get_contract(source) if field.required}


def allowed_values_for(source: SourceContract, field_name: str) -> set[str]:
    """Return allowed values for a controlled field."""

    return ALLOWED_VALUES.get(source, {}).get(field_name, set())
