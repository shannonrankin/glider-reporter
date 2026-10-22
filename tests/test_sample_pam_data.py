from pathlib import Path
import subprocess
import tempfile
import unittest

import h5py
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPOSITORY_ROOT / "scripts/generate_sample_pam_data.py"
EXPECTED_COLUMNS = [
    "time_utc",
    "frequency_hz",
    "hmd_db_re_1_upa_squared_per_hz",
    "spl_db_re_1_upa",
]
SAMPLE_TIME_COLUMNS = {
    "og10": (
        REPOSITORY_ROOT / "data/sample/og10_standard/glider_og10_data.csv",
        "time",
    ),
    "hackathon": (
        REPOSITORY_ROOT / "data/sample/custom_hackathon/glider_hackathon_data.csv",
        "ISO-Time",
    ),
}


class SamplePamDataTests(unittest.TestCase):
    def test_generator_writes_yawn_layout_and_long_spectra(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            subprocess.run(
                ["python", str(GENERATOR), "--output-directory", str(output_directory)],
                check=True,
                cwd=REPOSITORY_ROOT,
            )

            for dataset_name in ("og10", "hackathon"):
                with h5py.File(output_directory / f"pam_noise_{dataset_name}.h5") as handle:
                    instrument = handle["GLIDER_01"]
                    self.assertEqual(
                        set(instrument),
                        {
                            "DateTime",
                            "Files",
                            "broadbandLevels",
                            "hybridDecFreqHz",
                            "hybridMiliDecLevels",
                        },
                    )
                    self.assertEqual(instrument["DateTime"].shape, (60,))
                    self.assertEqual(
                        instrument["DateTime"].asstr()[:].tolist(),
                        pd.read_csv(SAMPLE_TIME_COLUMNS[dataset_name][0])[
                            SAMPLE_TIME_COLUMNS[dataset_name][1]
                        ].tolist(),
                    )
                    self.assertEqual(instrument["hybridDecFreqHz"][0], 10)
                    self.assertEqual(instrument["hybridDecFreqHz"][-1], 10_000)
                    self.assertEqual(instrument["hybridMiliDecLevels"].shape, (60, 31))
                    self.assertTrue(
                        ((instrument["hybridMiliDecLevels"][:] >= 50)
                        & (instrument["hybridMiliDecLevels"][:] <= 120)).all()
                    )

                spectrum = pd.read_parquet(
                    output_directory / f"pam_spectrum_{dataset_name}.parquet"
                )
                source_path, source_time_column = SAMPLE_TIME_COLUMNS[dataset_name]
                source_timestamps = pd.read_csv(source_path)[source_time_column].tolist()
                self.assertEqual(list(spectrum), EXPECTED_COLUMNS)
                self.assertEqual(len(spectrum), 60 * 31)
                self.assertEqual(spectrum["time_utc"].nunique(), 60)
                self.assertEqual(
                    spectrum["time_utc"].iloc[::31].tolist(), source_timestamps
                )
                self.assertTrue(spectrum["frequency_hz"].between(10, 10_000).all())


if __name__ == "__main__":
    unittest.main()
