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

# Helpers

def run_recent_workouts(workouts_list) -> AppTest:
    """Create a fresh test app session for display_recent_workouts and run once."""
    at = AppTest.from_string(f"""
import streamlit as st
import modules

modules.st = st

# Capture rendered cards
st.session_state["rendered_cards"] = []

def spy_create_component(data, component_name, height, width):
    st.session_state["rendered_cards"].append({{
        "data": data,
        "component_name": component_name,
        "height": height,
        "width": width,
    }})

modules.create_component = spy_create_component

modules.display_recent_workouts({repr(workouts_list)})
""").run()

    assert not at.exception
    return at


def ss_get(at: AppTest, key: str, default=None):
    """Safe session_state getter.

    Streamlit's AppTest exposes session_state as a proxy (not a dict), so
    dict-style helpers like `.get()` may not exist.
    """
    try:
        if key in at.session_state:
            return at.session_state[key]
    except Exception:
        pass

    try:
        return at.session_state[key]
    except Exception:
        return default
        
# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""
    def test_foo(self):
        """Tests foo."""
    pass

class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_empty_list_shows_info_message(self):
        at = run_recent_workouts([])

        self.assertGreaterEqual(len(at.info), 1)
        self.assertEqual(at.info[0].value, "No recent workouts found.")

    def test_non_empty_list_renders_one_card(self):
        workouts = [{
            "start_timestamp": "2024-01-01 00:00:00",
            "end_timestamp": "2024-01-01 00:30:00",
            "distance": 5.0,
            "steps": 1000,
            "calories_burned": 200,
            "start_lat_lng": [1.0, 2.0],
            "end_lat_lng": [3.0, 4.0],
        }]

        at = run_recent_workouts(workouts)
        rendered = ss_get(at, "rendered_cards", [])

        self.assertEqual(len(rendered), 1)

    def test_card_data_mapping_is_correct(self):
        workouts = [{
            "start_timestamp": "2024-01-01 00:00:00",
            "end_timestamp": "2024-01-01 00:30:00",
            "distance": 20.0,
            "steps": 5760,
            "calories_burned": 34,
            "start_lat_lng": [1.07, 4.45],
            "end_lat_lng": [1.06, 4.55],
        }]

        at = run_recent_workouts(workouts)
        rendered = ss_get(at, "rendered_cards", [])
        card = rendered[0]

        expected_data = {
            "START_TIME": "2024-01-01 00:00:00",
            "END_TIME": "2024-01-01 00:30:00",
            "DISTANCE": "20.0 km",
            "STEPS": 5760,
            "CALORIES": 34,
            "START_COORDS": "1.07, 4.45",
            "END_COORDS": "1.06, 4.55",
        }

        self.assertEqual(card["component_name"], "workout_card")
        self.assertEqual(card["height"], 270)
        self.assertEqual(card["width"], 500)
        self.assertEqual(card["data"], expected_data)

if __name__ == "__main__":
    unittest.main()
