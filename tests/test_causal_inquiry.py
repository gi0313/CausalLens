import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.causal_inquiry import (
    build_fd001_causal_inquiry,
    save_causal_inquiry,
    validate_causal_inquiry
)

class TestCausalInquiry(unittest.TestCase):

    # Confirms that the normal builder produces the intended status
    # and leaves the unevaluated result fields empty.
    def test_builds_an_unevaluated_inquiry(self):
        inquiry = build_fd001_causal_inquiry()

        self.assertEqual(
            inquiry["dataset"]["subset"],
            "FD001"
        )
        self.assertEqual(
            inquiry["analysis"]["status"],
            "not_evaluated"
        )
        self.assertFalse(
            inquiry["analysis"]["causal_direction_established"]
        )
        self.assertIsNone(
            inquiry["analysis"]["method"]
        )
        self.assertIsNone(
            inquiry["analysis"]["effect_estimate"]
        )

    # Confirms the output uses P30, T30, and the HPC component.
    def test_uses_the_shared_sensor_catalog(self):
        inquiry = build_fd001_causal_inquiry()

        self.assertEqual(
            inquiry["candidate_source"]["symbol"],
            "P30"
        )
        self.assertEqual(
            inquiry["target"]["symbol"],
            "T30"
        )
        self.assertEqual(
            inquiry["candidate_source"]["component"],
            "HPC"
        )
        self.assertEqual(
            inquiry["target"]["component"],
            "HPC"
        )

    # Confirms invalid elationships with self are rejected.
    def test_rejects_the_same_source_and_target(self):
        with self.assertRaises(ValueError):
            build_fd001_causal_inquiry(
                candidate_source = "hpc_exit_temperature",
                target = "hpc_exit_temperature"
            )

    # Confirms invented or misspelled measurements cannot enter the contract.
    def test_rejects_an_unknown_measurement(self):
        with self.assertRaises(ValueError):
            build_fd001_causal_inquiry(
                candidate_source = "not_a_real_measurement",
                target = "hpc_exit_temperature"
            )

    # Deliberately inserts an effect estimate into an unevaluated inquiry
    # to test that it is rejected.
    def test_rejects_a_result_added_before_evaluation(self):
        inquiry = build_fd001_causal_inquiry()
        inquiry["analysis"]["effect_estimate"] = 1.25

        with self.assertRaises(ValueError):
            validate_causal_inquiry(inquiry)

    # Builds an inquiry, creates temp folder, writes the JSON,
    # reads it back, and confirms its important fields survived.
    def test_saves_readable_json(self):
        inquiry = build_fd001_causal_inquiry()

        with TemporaryDirectory() as temporary_directory:
            output_path = (
                Path(temporary_directory)
                / "inquiry.json"
            )

            saved_path = save_causal_inquiry(
                inquiry, 
                output_path
            )
            
            # Converts contents of saved JSON file into python dictionary.
            loaded = json.loads(
                saved_path.read_text(
                    encoding = "utf-8"
                )
            )

        self.assertEqual(
            loaded["inquiry_id"],
            inquiry["inquiry_id"]
        )
        self.assertEqual(
            loaded["analysis"]["status"],
            "not_evaluated"
        )

if __name__ == "__main__":
    unittest.main()