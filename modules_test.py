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
from unittest.mock import patch

# -------------------------
# Helpers 
# -------------------------

def run_display_post(username, user_image, timestamp, content, post_image) -> AppTest:
    """Create a fresh test app session for display_post and run once.""" #
    at = AppTest.from_string(f"""
import streamlit as st 
import modules

modules.st = st #Line written by ChatGPT
st.session_state["rendered_posts"] = [] #Line written by ChatGPT

def spy_create_component(data, html_file_name, **kwargs): #Line written by ChatGPT
    st.session_state["rendered_posts"].append({{ #Line written by ChatGPT
        "data": data,  #Line written by ChatGPT
        "html_file_name": html_file_name, #Line written by ChatGPT
        "kwargs": kwargs, #Line written by ChatGPT
    }})

modules.create_component = spy_create_component #Line written by ChatGPT

modules.display_post( #Line written by ChatGPT
    {username!r}, #Line written by ChatGPT
    {user_image!r}, #Line written by ChatGPT
    {timestamp!r}, #Line written by ChatGPT
    {content!r}, #Line written by ChatGPT
    {post_image!r}, #Line written by ChatGPT
)
""", default_timeout=10).run() #Line written by ChatGPT

    assert not at.exception #Line written by ChatGPT
    return at #Line written by ChatGPT


def run_recent_workouts(workouts_list) -> AppTest:
    """Create a fresh test app session for display_recent_workouts and run once."""
    at = AppTest.from_string(f"""
import streamlit as st
import modules

modules.st = st

# Capture rendered cards
st.session_state["rendered_cards"] = [] #Line written by ChatGPT

def spy_create_component(data, component_name, height, width): #Line written by ChatGPT
    st.session_state["rendered_cards"].append({{ #Line written by ChatGPT
        "data": data, #Line written by ChatGPT
        "component_name": component_name, #Line written by ChatGPT
        "height": height, #Line written by ChatGPT
        "width": width, #Line written by ChatGPT
    }})

modules.create_component = spy_create_component #Line written by ChatGPT

modules.display_recent_workouts({repr(workouts_list)})
""").run() #Line written by ChatGPT

    assert not at.exception #Line written by ChatGPT
    return at #Line written by ChatGPT


def ss_get(at: AppTest, key: str, default=None): 
    """Safe session_state getter."""
    try:
        if key in at.session_state:
            return at.session_state[key]
    except Exception:
        pass

    try:
        return at.session_state[key]
    except Exception:
        return default

# -------------------------
# Tests 
# -------------------------

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_renders_post_correctly(self):
        at = run_display_post(
            "dumblesdore",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJy3l6QYwrg0C6mh8Eo9_gmx97cZF5MyRe_g&s",
            "2024-01-01 00:00:00",
            "HARRY DID YOU PUT YOUR NAME IN THE GOBLET OF FIRE",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJyeF5NIhpNDVUnxcs0DzhsOuq9lqk30A9xQ&s",
        )

        rendered = ss_get(at, "rendered_posts", [])
        self.assertEqual(len(rendered), 1)

    def test_post_data_mapping_is_correct(self):
        username = "dumblesdore"
        user_image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJy3l6QYwrg0C6mh8Eo9_gmx97cZF5MyRe_g&s"
        timestamp = "2024-01-01 00:00:00"
        content = "HARRY DID YOU PUT YOUR NAME IN THE GOBLET OF FIRE"
        post_image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJyeF5NIhpNDVUnxcs0DzhsOuq9lqk30A9xQ&s"

        at = run_display_post(username, user_image, timestamp, content, post_image)
        rendered = ss_get(at, "rendered_posts", [])
        post = rendered[0]

        expected_data = {
            "USERNAME": username,
            "USER_IMAGE": user_image,
            "TIMESTAMP": timestamp,
            "CONTENT": content,
            "POST_IMAGE": post_image,
        }

        self.assertEqual(post["html_file_name"], "posts")
        self.assertEqual(post["data"], expected_data)
        self.assertEqual(post["kwargs"].get("height"), 500)
        self.assertEqual(post["kwargs"].get("scrolling"), True)

    def test_empty_post_image(self):
        at = run_display_post(
            "dumblesdore",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJy3l6QYwrg0C6mh8Eo9_gmx97cZF5MyRe_g&s",
            "2024-01-01 00:00:00",
            "HARRY DID YOU PUT YOUR NAME IN THE GOBLET OF FIRE",
            "",
        )

        rendered = ss_get(at, "rendered_posts", [])
        post = rendered[0]
        self.assertEqual(post["data"]["POST_IMAGE"], "")

    def test_empty_profile_image(self):
        at = run_display_post(
            "dumblesdore",
            "",
            "2024-01-01 00:00:00",
            "HARRY DID YOU PUT YOUR NAME IN THE GOBLET OF FIRE",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJyeF5NIhpNDVUnxcs0DzhsOuq9lqk30A9xQ&s",
        )

        rendered = ss_get(at, "rendered_posts", [])
        post = rendered[0]
        self.assertEqual(post["data"]["USER_IMAGE"], "")

    def test_empty_content(self):
        at = run_display_post(
            "dumblesdore",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJy3l6QYwrg0C6mh8Eo9_gmx97cZF5MyRe_g&s",
            "2024-01-01 00:00:00",
            "",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJyeF5NIhpNDVUnxcs0DzhsOuq9lqk30A9xQ&s",
        )

        rendered = ss_get(at, "rendered_posts", [])
        post = rendered[0]
        self.assertEqual(post["data"]["CONTENT"], "")

    def test_empty_time_stamp(self):
        at = run_display_post(
            "dumblesdore",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJy3l6QYwrg0C6mh8Eo9_gmx97cZF5MyRe_g&s",
            "2024-01-01 00:00:00",
            "",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJyeF5NIhpNDVUnxcs0DzhsOuq9lqk30A9xQ&s",
        )

        rendered = ss_get(at, "rendered_posts", [])
        post = rendered[0]
        self.assertEqual(post["data"]["CONTENT"], "")

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""
   
    def test_totals_computed_correctly(self):
        """TOTAL_WORKOUTS, TOTAL_CALORIES, and TOTAL_DURATION are computed
        correctly from real data_fetcher keys (calories_burned + timestamps)."""
        workouts = [
            {
                'calories_burned': 80,
                'start_timestamp': '2024-01-01 00:00:00',
                'end_timestamp':   '2024-01-01 00:30:00',  # 30 min
            },
            {
                'calories_burned': 60,
                'start_timestamp': '2024-01-02 00:00:00',
                'end_timestamp':   '2024-01-02 01:00:00',  # 60 min
            },
        ]
        with patch('modules.create_component') as mock_cc:
            display_activity_summary(workouts)
            data, _ = mock_cc.call_args[0]

        self.assertEqual(data['TOTAL_WORKOUTS'], 2)
        self.assertEqual(data['TOTAL_CALORIES'], 140)
        self.assertEqual(data['TOTAL_DURATION'], 90)   # 30 + 60 minutes



class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def setUp(self):
        """Sets up common test variables."""
        self.valid_timestamp = "2026-02-23 23:59:52"
        self.valid_content = "Increase weight slightly while maintaining strict form."
        self.valid_image = "https://example.com/image.jpg"

    @patch("modules.create_component")
    def test_display_genai_advice_calls_create_component_once_none(self, mock_create):
        """Tests create_component is called exactly once and returns None."""
        result = display_genai_advice(
            self.valid_timestamp,
            self.valid_content,
            self.valid_image
        )

        mock_create.assert_called_once()
        self.assertIsNone(result)

    @patch("modules.create_component")
    def test_display_genai_advice_passes_correct_data_dictionary_none(self, mock_create):
        """Tests correct data dictionary is passed to create_component."""
        display_genai_advice(
            self.valid_timestamp,
            self.valid_content,
            self.valid_image
        )

        expected_data = {
            'TIMESTAMP': self.valid_timestamp,
            'CONTENT': self.valid_content,
            'IMAGE': self.valid_image
        }

        mock_create.assert_called_once_with(
            expected_data,
            'display_genai_advice_component',
            height=250,
            scrolling=True
        )

    @patch("modules.create_component")
    def test_display_genai_advice_handles_empty_strings_none(self, mock_create):
        """Tests function handles empty string inputs."""
        display_genai_advice("", "", "")

        expected_data = {
            'TIMESTAMP': "",
            'CONTENT': "",
            'IMAGE': ""
        }

        mock_create.assert_called_once_with(
            expected_data,
            'display_genai_advice_component',
            height=250,
            scrolling=True
        )

    @patch("modules.create_component")
    def test_display_genai_advice_handles_none_inputs_none(self, mock_create):
        """Tests function handles None inputs."""
        display_genai_advice(None, None, None)

        expected_data = {
            'TIMESTAMP': None,
            'CONTENT': None,
            'IMAGE': None
        }

        mock_create.assert_called_once_with(
            expected_data,
            'display_genai_advice_component',
            height=250,
            scrolling=True
        )

    @patch("modules.create_component")
    def test_display_genai_advice_handles_long_content_none(self, mock_create):
        """Tests function handles very long content string."""
        long_content = "A" * 10000

        display_genai_advice(
            self.valid_timestamp,
            long_content,
            self.valid_image
        )

        expected_data = {
            'TIMESTAMP': self.valid_timestamp,
            'CONTENT': long_content,
            'IMAGE': self.valid_image
        }

        mock_create.assert_called_once_with(
            expected_data,
            'display_genai_advice_component',
            height=250,
            scrolling=True
        )

    @patch("modules.create_component")
    def test_display_genai_advice_uses_correct_component_name_none(self, mock_create):
        display_genai_advice(
            self.valid_timestamp,
            self.valid_content,
            self.valid_image
        )

        args, kwargs = mock_create.call_args
        self.assertEqual(args[1], "display_genai_advice_component")

    @patch("modules.create_component")
    def test_display_genai_advice_contains_required_keys_none(self, mock_create):
        display_genai_advice(
            self.valid_timestamp,
            self.valid_content,
            self.valid_image
        )

        args, _ = mock_create.call_args
        data_dict = args[0]

        self.assertIn("TIMESTAMP", data_dict)
        self.assertIn("CONTENT", data_dict)
        self.assertIn("IMAGE", data_dict)

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_empty_list_shows_info_message(self):
        at = run_recent_workouts([])

        self.assertGreaterEqual(len(at.info), 1)
        self.assertEqual(at.info[0].value, "No recent workouts found.")

    def test_non_empty_list_renders_one_card(self):
        workouts = [{
            "workout_id": "workout_1",
            "start_timestamp": "2024-01-01 00:00:00",
            "end_timestamp": "2024-01-01 00:30:00",
            "distance": 5.0,
            "steps": 1000,
            "calories_burned": 200,
            "start_lat_lng": (1.0, 2.0), 
            "end_lat_lng": (3.0, 4.0),  
        }]

        at = run_recent_workouts(workouts)
        rendered = ss_get(at, "rendered_cards", [])

        self.assertEqual(len(rendered), 1)

    def test_card_data_mapping_is_correct(self):
        workouts = [{
            "workout_id": "workout_full",
            "start_timestamp": "2024-01-01 00:00:00",
            "end_timestamp": "2024-01-01 00:30:00",
            "distance": 20.0,
            "steps": 5760,
            "calories_burned": 34,
            "start_lat_lng": (1.07, 4.45),
            "end_lat_lng": (1.06, 4.55),
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

        # Validate component metadata and content mapping
        self.assertEqual(card["component_name"], "workout_card")
        self.assertEqual(card["height"], 270) 
        self.assertEqual(card["width"], 500)
        self.assertEqual(card["data"], expected_data)

    def test_multiple_workouts_render_multiple_cards(self):
        workouts = [
            {"workout_id": "w1", "start_timestamp": "...", "end_timestamp": "...", "distance": 1.0, 
             "steps": 100, "calories_burned": 10, "start_lat_lng": (0,0), "end_lat_lng": (0,0)},
            {"workout_id": "w2", "start_timestamp": "...", "end_timestamp": "...", "distance": 2.0, 
             "steps": 200, "calories_burned": 20, "start_lat_lng": (0,0), "end_lat_lng": (0,0)}
        ]
        
        at = run_recent_workouts(workouts)
        rendered = ss_get(at, "rendered_cards", [])
        self.assertEqual(len(rendered), 2)

if __name__ == "__main__":
    unittest.main()
    