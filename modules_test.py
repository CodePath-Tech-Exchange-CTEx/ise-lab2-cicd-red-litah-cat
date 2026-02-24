#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""
   
    def test_totals_computed_correctly(self):
        """Workouts, calories, and duration are summed correctly from the list."""
        workouts = [
            {'name': 'Running',  'date': 'Mar 15, 2024', 'calories': 450, 'duration': 35},
            {'name': 'Cycling',  'date': 'Mar 14, 2024', 'calories': 380, 'duration': 45},
            {'name': 'Swimming', 'date': 'Mar 13, 2024', 'calories': 300, 'duration': 30},
        ]
        with patch('modules.create_component') as mock_cc:
            display_activity_summary(workouts)
            data, _ = mock_cc.call_args[0]

        self.assertEqual(data['TOTAL_WORKOUTS'], 3)
        self.assertEqual(data['TOTAL_CALORIES'], 1130)
        self.assertEqual(data['TOTAL_DURATION'], 110)


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
