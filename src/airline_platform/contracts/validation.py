"""Simple contract validation for raw payload records."""

import re
from collections.abc import Mapping
from datetime import datetime

from airline_platform.contracts.schemas import (
    SourceContract,
    allowed_values_for,
    get_contract,
    required_field_names,
)

IATA_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")


def validate_required_fields(
    source: SourceContract,
    records: list[Mapping[str, object]],
) -> list[str]:
    """Validate required fields and return human-readable errors."""

    required_fields = required_field_names(source)
    errors: list[str] = []

    for index, record in enumerate(records):
        missing_fields = sorted(required_fields.difference(record.keys()))
        if missing_fields:
            fields = ", ".join(missing_fields)
            errors.append(f"{source.value}[{index}] missing required field(s): {fields}")

    return errors


def validate_contract(
    source: SourceContract,
    records: list[Mapping[str, object]],
) -> list[str]:
    """Validate required fields and basic source-specific business rules."""

    errors = validate_required_fields(source, records)

    for index, record in enumerate(records):
        errors.extend(_validate_non_empty_required_fields(source, index, record))
        errors.extend(_validate_controlled_values(source, index, record))
        errors.extend(_validate_timestamps(source, index, record))

        if source is SourceContract.FLIGHTS:
            errors.extend(_validate_flight_record(index, record))
        elif source is SourceContract.AIRPORTS:
            errors.extend(_validate_airport_record(index, record))
        elif source is SourceContract.WEATHER:
            errors.extend(_validate_weather_record(index, record))

    return errors


def _validate_non_empty_required_fields(
    source: SourceContract,
    index: int,
    record: Mapping[str, object],
) -> list[str]:
    errors: list[str] = []

    for field_name in required_field_names(source):
        if field_name in record and _is_blank(record[field_name]):
            errors.append(f"{source.value}[{index}] required field is empty: {field_name}")

    return errors


def _validate_controlled_values(
    source: SourceContract,
    index: int,
    record: Mapping[str, object],
) -> list[str]:
    errors: list[str] = []

    for field in get_contract(source):
        allowed_values = allowed_values_for(source, field.name)
        if not allowed_values or field.name not in record or _is_blank(record[field.name]):
            continue

        value = str(record[field.name])
        if value not in allowed_values:
            allowed = ", ".join(sorted(allowed_values))
            errors.append(
                f"{source.value}[{index}] invalid value for {field.name}: {value}. "
                f"Allowed values: {allowed}"
            )

    return errors


def _validate_timestamps(
    source: SourceContract,
    index: int,
    record: Mapping[str, object],
) -> list[str]:
    errors: list[str] = []

    for field in get_contract(source):
        if field.dtype != "timestamp" or field.name not in record or _is_blank(record[field.name]):
            continue

        if not _is_parseable_utc_timestamp(record[field.name]):
            errors.append(
                f"{source.value}[{index}] invalid UTC timestamp for {field.name}: "
                f"{record[field.name]}"
            )

    return errors


def _validate_flight_record(index: int, record: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    for field_name in ("origin_airport", "destination_airport"):
        if (
            field_name in record
            and not _is_blank(record[field_name])
            and not _is_iata_code(record[field_name])
        ):
            errors.append(f"flights[{index}] invalid IATA airport code for {field_name}")

    return errors


def _validate_airport_record(index: int, record: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    if (
        "airport_code" in record
        and not _is_blank(record["airport_code"])
        and not _is_iata_code(record["airport_code"])
    ):
        errors.append(f"airports[{index}] invalid IATA airport code for airport_code")

    coordinate_ranges = {
        "latitude_deg": (-90.0, 90.0),
        "longitude_deg": (-180.0, 180.0),
    }
    for field_name, (minimum, maximum) in coordinate_ranges.items():
        if field_name not in record or _is_blank(record[field_name]):
            continue
        if not _is_number_in_range(record[field_name], minimum, maximum):
            errors.append(
                f"airports[{index}] invalid numeric range for {field_name}: {record[field_name]}"
            )

    return errors


def _validate_weather_record(index: int, record: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    if (
        "airport_code" in record
        and not _is_blank(record["airport_code"])
        and not _is_iata_code(record["airport_code"])
    ):
        errors.append(f"weather[{index}] invalid IATA airport code for airport_code")

    numeric_ranges = {
        "temperature_c": (-80.0, 60.0),
        "wind_speed_kmh": (0.0, 400.0),
        "precipitation_mm": (0.0, 500.0),
    }
    for field_name, (minimum, maximum) in numeric_ranges.items():
        if field_name not in record or _is_blank(record[field_name]):
            continue
        if not _is_number_in_range(record[field_name], minimum, maximum):
            errors.append(
                f"weather[{index}] invalid numeric range for {field_name}: {record[field_name]}"
            )

    return errors


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _is_iata_code(value: object) -> bool:
    return isinstance(value, str) and IATA_CODE_PATTERN.fullmatch(value) is not None


def _is_parseable_utc_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False

    return value.endswith("Z") or value.endswith("+00:00")


def _is_number_in_range(value: object, minimum: float, maximum: float) -> bool:
    if isinstance(value, bool):
        return False

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False

    return minimum <= numeric_value <= maximum
