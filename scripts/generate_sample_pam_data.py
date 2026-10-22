"""Generate deterministic YAWN-compatible sample PAM data."""

from argparse import ArgumentParser
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATASETS = {
    "og10": (
        "data/sample/og10_standard/glider_og10_data.csv",
        {"time": "time"},
    ),
    "hackathon": (
        "data/sample/custom_hackathon/glider_hackathon_data.csv",
        {"time": "ISO-Time"},
    ),
}
INSTRUMENT_NAME = "GLIDER_01"
FREQUENCIES_HZ = np.geomspace(10, 10_000, 31).round(2)


def create_levels(record_count: int) -> tuple[np.ndarray, np.ndarray]:
    """Create ambient-ocean hybrid spectrum and broadband SPL levels."""
    time_index = np.arange(record_count, dtype=float)[:, np.newaxis]
    frequency_index = np.log10(FREQUENCIES_HZ / FREQUENCIES_HZ[0])[np.newaxis, :]
    hmd_levels = 93 - (11 * frequency_index) + (4 * np.sin(time_index / 7))
    hmd_levels += 2 * np.cos(time_index / 11 + frequency_index * 5)
    hmd_levels = np.clip(hmd_levels, 50, 120).round(2)
    spl_levels = np.clip(108 + 4 * np.sin(np.arange(record_count) / 8), 50, 120)
    return hmd_levels, spl_levels.round(2)


def write_hdf5(
    output_path: Path,
    timestamps: pd.Series,
    hmd_levels: np.ndarray,
    spl_levels: np.ndarray,
) -> None:
    """Write the YAWN_functions time-by-frequency HDF5 layout."""
    string_dtype = h5py.string_dtype(encoding="utf-8")
    with h5py.File(output_path, "w") as handle:
        instrument = handle.create_group(INSTRUMENT_NAME)
        instrument.create_dataset(
            "DateTime",
            data=timestamps.astype(str).to_numpy(dtype=object),
            dtype=string_dtype,
        )
        instrument.create_dataset("hybridDecFreqHz", data=FREQUENCIES_HZ)
        instrument.create_dataset("hybridMiliDecLevels", data=hmd_levels)
        instrument.create_dataset("broadbandLevels", data=spl_levels)
        instrument.create_dataset(
            "Files",
            data=np.array(
                [f"synthetic_pam_{index:03d}.wav" for index in range(len(timestamps))],
                dtype=object,
            ),
            dtype=string_dtype,
        )


def write_parquet(
    output_path: Path,
    timestamps: pd.Series,
    hmd_levels: np.ndarray,
    spl_levels: np.ndarray,
) -> None:
    """Write the long-form equivalent of YAWN's time-by-frequency HDF5 data."""
    spectrum = pd.DataFrame(
        {
            "time_utc": np.repeat(timestamps.astype(str).to_numpy(), len(FREQUENCIES_HZ)),
            "frequency_hz": np.tile(FREQUENCIES_HZ, len(timestamps)),
            "hmd_db_re_1_upa_squared_per_hz": hmd_levels.ravel(),
            "spl_db_re_1_upa": np.repeat(spl_levels, len(FREQUENCIES_HZ)),
        }
    )
    spectrum.to_parquet(output_path, index=False)


def generate_sample_pam_data(output_directory: Path) -> None:
    """Generate HDF5 and Parquet PAM fixtures for each glider sample schema."""
    output_directory.mkdir(parents=True, exist_ok=True)
    for dataset_name, (relative_path, columns) in SAMPLE_DATASETS.items():
        glider_data = pd.read_csv(REPOSITORY_ROOT / relative_path)
        timestamps = glider_data[columns["time"]]
        hmd_levels, spl_levels = create_levels(len(glider_data))
        write_hdf5(
            output_directory / f"pam_noise_{dataset_name}.h5",
            timestamps,
            hmd_levels,
            spl_levels,
        )
        write_parquet(
            output_directory / f"pam_spectrum_{dataset_name}.parquet",
            timestamps,
            hmd_levels,
            spl_levels,
        )


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=REPOSITORY_ROOT / "data/sample",
        help="Directory for generated PAM files (default: data/sample).",
    )
    arguments = parser.parse_args()
    generate_sample_pam_data(arguments.output_directory)
