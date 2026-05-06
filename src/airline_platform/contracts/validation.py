"""Simple contract validation for raw payload records."""

from collections.abc import Mapping

from airline_platform.contracts.schemas import SourceContract, required_field_names


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

