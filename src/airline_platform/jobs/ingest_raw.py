"""Raw ingestion job for local API-like and synthetic source payloads."""

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

from airline_platform.contracts import SourceContract
from airline_platform.contracts.validation import validate_contract
from airline_platform.extractors import (
    SyntheticAirlineData,
    build_synthetic_data,
    fetch_openmeteo_weather_for_airports,
    fetch_ourairports_airports,
)


@dataclass(frozen=True)
class SourceValidationSummary:
    """Validation outcome for one source dataset."""

    source: str
    accepted_records: int
    rejected_records: int
    errors: list[str]


@dataclass(frozen=True)
class RawIngestionSummary:
    """Summary produced by the raw ingestion job."""

    output_dir: str
    sources: list[SourceValidationSummary]

    @property
    def total_accepted_records(self) -> int:
        """Return accepted record count across all sources."""

        return sum(source.accepted_records for source in self.sources)

    @property
    def total_rejected_records(self) -> int:
        """Return rejected record count across all sources."""

        return sum(source.rejected_records for source in self.sources)


def ingest_synthetic_raw(output_dir: Path) -> RawIngestionSummary:
    """Validate synthetic fallback data and write accepted raw JSON files."""

    synthetic_data = build_synthetic_data()
    source_records = _source_records_from_synthetic_data(synthetic_data)
    return ingest_raw_records(source_records, output_dir)


def ingest_raw_with_airport_source(
    output_dir: Path,
    airport_source: str = "synthetic",
    weather_source: str = "synthetic",
    weather_start_date: str = "2026-05-06",
    weather_end_date: str = "2026-05-06",
) -> RawIngestionSummary:
    """Run raw ingestion with synthetic data and optional public enrichments."""

    synthetic_data = build_synthetic_data()
    source_records = _source_records_from_synthetic_data(synthetic_data)

    if airport_source == "ourairports":
        try:
            source_records[SourceContract.AIRPORTS] = fetch_ourairports_airports()
        except Exception:
            # Keep the portfolio demo deterministic even when public data is unavailable.
            source_records[SourceContract.AIRPORTS] = synthetic_data.airports
    elif airport_source != "synthetic":
        message = f"Unsupported airport source: {airport_source}"
        raise ValueError(message)

    if weather_source == "openmeteo":
        try:
            source_records[SourceContract.WEATHER] = fetch_openmeteo_weather_for_airports(
                source_records[SourceContract.AIRPORTS],
                start_date=weather_start_date,
                end_date=weather_end_date,
            )
        except Exception:
            # Public weather enrichment is optional; synthetic weather keeps demos stable.
            source_records[SourceContract.WEATHER] = synthetic_data.weather
    elif weather_source != "synthetic":
        message = f"Unsupported weather source: {weather_source}"
        raise ValueError(message)

    return ingest_raw_records(source_records, output_dir)


def ingest_raw_records(
    source_records: Mapping[SourceContract, list[dict[str, object]]],
    output_dir: Path,
) -> RawIngestionSummary:
    """Validate source records and write accepted raw records plus a summary."""

    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[SourceValidationSummary] = []

    for source, records in source_records.items():
        errors = validate_contract(source, records)
        accepted_records = [] if errors else records
        _write_json(output_dir / f"{source.value}.json", accepted_records)

        summaries.append(
            SourceValidationSummary(
                source=source.value,
                accepted_records=len(accepted_records),
                rejected_records=len(records) - len(accepted_records),
                errors=errors,
            )
        )

    summary = RawIngestionSummary(output_dir=str(output_dir), sources=summaries)
    _write_json(output_dir / "validation_summary.json", asdict(summary))
    return summary


def main() -> None:
    """Run raw ingestion from the command line."""

    parser = argparse.ArgumentParser(
        description="Ingest synthetic fallback data into the raw layer."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory where raw JSON files and validation summary will be written.",
    )
    parser.add_argument(
        "--airport-source",
        choices=("synthetic", "ourairports"),
        default="synthetic",
        help="Airport metadata source. Defaults to deterministic synthetic fallback.",
    )
    parser.add_argument(
        "--weather-source",
        choices=("synthetic", "openmeteo"),
        default="synthetic",
        help="Weather source. Defaults to deterministic synthetic fallback.",
    )
    parser.add_argument(
        "--weather-start-date",
        default="2026-05-06",
        help="Open-Meteo start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--weather-end-date",
        default="2026-05-06",
        help="Open-Meteo end date in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    summary = ingest_raw_with_airport_source(
        args.output_dir,
        airport_source=args.airport_source,
        weather_source=args.weather_source,
        weather_start_date=args.weather_start_date,
        weather_end_date=args.weather_end_date,
    )
    print(
        "Raw ingestion finished: "
        f"{summary.total_accepted_records} accepted, "
        f"{summary.total_rejected_records} rejected."
    )


def _source_records_from_synthetic_data(
    synthetic_data: SyntheticAirlineData,
) -> dict[SourceContract, list[dict[str, object]]]:
    return {
        SourceContract.FLIGHTS: synthetic_data.flights,
        SourceContract.AIRPORTS: synthetic_data.airports,
        SourceContract.WEATHER: synthetic_data.weather,
        SourceContract.PASSENGER_EVENTS: synthetic_data.passenger_events,
    }


def _write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")


if __name__ == "__main__":
    main()
