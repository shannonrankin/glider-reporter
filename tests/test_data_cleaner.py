import unittest

import pandas as pd

from python.data_cleaner import clean_glider_data


class CleanGliderDataTests(unittest.TestCase):
    def test_custom_headers_and_values_are_normalized(self):
        data = pd.DataFrame(
            {
                "Lat Deg": ["32.5"],
                "Lon-Deg": ["-118.2"],
                "ISO-Time": ["2024-06-01 12:00:00"],
            }
        )

        cleaned = clean_glider_data(data)

        self.assertEqual(list(cleaned.columns), ["lat_deg", "lon_deg", "iso_time"])
        self.assertEqual(cleaned["iso_time"].iloc[0], "2024-06-01T12:00:00Z")
        self.assertEqual(cleaned["lat_deg"].iloc[0], 32.5)
        self.assertTrue(cleaned.attrs["validation"]["valid"])

    def test_missing_essential_field_is_reported(self):
        cleaned = clean_glider_data(
            pd.DataFrame({"latitude": [32.5], "longitude": [-118.2]})
        )

        self.assertFalse(cleaned.attrs["validation"]["valid"])
        self.assertIn("missing essential column: time", cleaned.attrs["validation"]["errors"])


if __name__ == "__main__":
    unittest.main()
