import unittest
from unittest.mock import patch, mock_open
import json
import os
import main
import logging

logging.getLogger('main').setLevel(logging.CRITICAL)


class TestSaveAndLoadData(unittest.TestCase):

    # Setup of a sample weekly_planner
    def setUp(self):
        self.sample_data = {
            "Monday": [
                {
                    "title": "Morning Meeting",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "location": "Conference Room",
                    "description": "Discuss progress",
                    "completed": False
                }
            ],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": [],
            "metadata": {
                "completed_quests_count": 0
            }
        }
        # Reset the global weekly_planner
        main.reset_planner()
        # Associate weekly_planner with sample data
        main.weekly_planner = self.sample_data.copy()

    # Reset the global weekly_planner
    def tearDown(self):
        main.reset_planner()

    # Test to ensure that the save_data-function can correctly write to json
    @patch("main.open", new_callable=mock_open)
    def test_save_data(self, mock_file):
        main.save_data()
        # Check if the file was opened
        mock_file.assert_called_once_with("data.json", "w")
        # Check json-structure in the file
        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
        expected_data = json.dumps(self.sample_data, indent=4)
        # The written- and expected data are compared as JSON objects to avoid formatting issues
        self.assertEqual(json.loads(written_data), json.loads(expected_data))

    # Test behavior when given an empty file
    @patch('os.path.exists', return_value=True)
    @patch("main.open", new_callable=mock_open, read_data="")
    def test_load_data_with_empty_file(self, mock_open_mock, mock_exists_mock):
        # Simulation of an empty file
        mock_open_mock.return_value.read.return_value = ""
        main.load_data()
        # Ensure that the default structure is loaded
        self.assertEqual(main.weekly_planner["Monday"], [])
        self.assertEqual(main.weekly_planner["metadata"]["completed_quests_count"], 0)

    # Test the load_data-function when data-file doesn't exist
    @patch('os.path.exists', return_value=False)
    @patch("main.open", new_callable=mock_open, read_data="")
    def test_load_data_file_not_found(self, mock_open_mock, mock_exists_mock):
        main.load_data()
        # Ensure that the default structure is loaded
        self.assertEqual(main.weekly_planner["Monday"], [])
        self.assertEqual(main.weekly_planner["metadata"]["completed_quests_count"], 0)

    # Test the load_data-function can load a properly formatted json-file
    @patch('os.path.exists', return_value=True)
    @patch("main.open", new_callable=mock_open)
    def test_load_data_with_proper_file(self, mock_open_mock, mock_exists_mock):
        mock_open_mock.return_value.read.return_value = json.dumps(self.sample_data)
        main.load_data()
        # Ensure the data is correctly loaded
        self.assertEqual(main.weekly_planner, self.sample_data)

    # Integration test to ensure save_data and load_data function persistently
    def test_integration_save_and_load(self):
        # Save sample data
        with patch("main.open", new_callable=mock_open) as mock_file:
            main.save_data()
            written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
            expected_data = json.dumps(self.sample_data, indent=4)
            self.assertEqual(json.loads(written_data), json.loads(expected_data))

        # Simulate the function loading the data
        with patch('os.path.exists', return_value=True):
            with patch("main.open", new_callable=mock_open, read_data=json.dumps(self.sample_data)):
                main.load_data()
                # Ensure data remains the same after loading-process
                self.assertEqual(main.weekly_planner, self.sample_data)

    # Test to ensure that the reset-button correctly resets the data.json-document
    def test_reset_planner(self):
        # Create a weekly_planner and simulate the planner having quests
        main.weekly_planner = self.sample_data.copy()

        # Call reset-function
        main.reset_planner()

        # Structure of the expected output after reset-procedure
        expected_reset_data = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": [],
            "metadata": {
                "completed_quests_count": 0
            }
        }

        # Ensure planner was reset correctly and reverted to its default state (being empty)
        self.assertEqual(main.weekly_planner, expected_reset_data)


if __name__ == '__main__':
    unittest.main()
