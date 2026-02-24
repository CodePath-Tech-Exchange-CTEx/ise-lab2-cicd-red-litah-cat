#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
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

    def _call(self, workouts_list):
        """Helper: calls display_activity_summary and returns the data dict
        passed to create_component."""
        with patch('modules.create_component') as mock_cc:
            display_activity_summary(workouts_list)
            args, _ = mock_cc.call_args
            return args  # (data_dict, html_file_name)

    def test_correct_html_file(self):
        """create_component is called with the 'activity_summary' template."""
        with patch('modules.create_component') as mock_cc:
            display_activity_summary([])
            _, html_file = mock_cc.call_args[0]
        self.assertEqual(html_file, 'activity_summary')

    def test_empty_list_totals_are_zero(self):
        """An empty list produces zero for all three aggregate stats."""
        data, _ = self._call([])
        self.assertEqual(data['TOTAL_WORKOUTS'], 0)
        self.assertEqual(data['TOTAL_CALORIES'], 0)
        self.assertEqual(data['TOTAL_DURATION'], 0)



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
