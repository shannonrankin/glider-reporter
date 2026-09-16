"""Utilities for normalising glider data to OG1.0-compatible values."""

import re
from typing import Any

import pandas as pd


ESSENTIAL_COLUMNS = ("latitude", "longitude", "time")
ALIASES = {
    "latitude": ("latitude", "lat", "lat_deg", "latitude_deg"),
    "longitude": ("longitude", "lon", "lon_deg", "longitude_deg"),
    "time": ("time", "iso_time", "timestamp"),
}


def _snake_case(name: Any) -> str:
    """Return a strict snake_case field name."""
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name))
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value or "unnamed"


def _validation_report(data: pd.DataFrame) -> dict[str, Any]:
    """Check the essential OG1.0 fields and return a serialisable report."""
    errors = [
        f"missing essential column: {column}"
        for column in ESSENTIAL_COLUMNS
        if not any(alias in data.columns for alias in ALIASES[column])
    ]
    warnings = []
    for column in ESSENTIAL_COLUMNS:
        present = next((alias for alias in ALIASES[column] if alias in data.columns), None)
        if present and data[present].isna().any():
            warnings.append(f"{column} contains missing or malformed values")
    return {
        "valid": not errors and not warnings,
        "errors": errors,
        "warnings": warnings,
    }


def clean_glider_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names, timestamps, coordinates, and schema metadata.

    The cleaned frame is returned even when validation fails.  The explicit
    ``validation`` report is available at ``cleaned.attrs["validation"]``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    cleaned = df.copy()
    cleaned.columns = [_snake_case(column) for column in cleaned.columns]

    time_column = next((alias for alias in ALIASES["time"] if alias in cleaned.columns), None)
    if time_column:
        parsed_time = pd.to_datetime(cleaned[time_column], errors="coerce", utc=True)
        cleaned[time_column] = parsed_time.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        cleaned.loc[parsed_time.isna(), time_column] = pd.NA

    coordinate_columns = {
        coordinate: next(
            (alias for alias in aliases if alias in cleaned.columns), None
        )
        for coordinate, aliases in ALIASES.items()
        if coordinate in ("latitude", "longitude")
    }
    for coordinate, column in coordinate_columns.items():
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if coordinate_columns.get("latitude"):
        column = coordinate_columns["latitude"]
        cleaned.loc[~cleaned[column].between(-90, 90), column] = pd.NA
    if coordinate_columns.get("longitude"):
        column = coordinate_columns["longitude"]
        cleaned.loc[~cleaned[column].between(-180, 180), column] = pd.NA

    cleaned.attrs["validation"] = _validation_report(cleaned)
    return cleaned
