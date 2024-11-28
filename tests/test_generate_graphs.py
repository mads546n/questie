import unittest
from unittest.mock import patch
import base64
import main


class TestGenerateGraphs(unittest.TestCase):
    def test_generate_graphs(self):
        # Create mock performance data
        performance_data = {
            'quests_per_day': {
                'Monday': {'total': 2, 'completed': 1},
                'Tuesday': {'total': 0, 'completed': 0},
                'Wednesday': {'total': 1, 'completed': 1},
                'Thursday': {'total': 3, 'completed': 2},
                'Friday': {'total': 0, 'completed': 0},
                'Saturday': {'total': 1, 'completed': 0},
                'Sunday': {'total': 0, 'completed': 0}
            }
        }

        graph_urls = main.generate_graphs(performance_data)

        # Ensure keys exist
        self.assertIn('total_quests', graph_urls)
        self.assertIn('completed_quests', graph_urls)

        # Ensure values are base64 strings
        total_quests_graph = graph_urls['total_quests']
        completed_quests_graph = graph_urls['completed_quests']

        try:
            base64.b64decode(total_quests_graph)
            base64.b64decode(completed_quests_graph)
        except base64.binascii.Error:
            self.fail("Graphs are not valid Base64-encoded strings!")
