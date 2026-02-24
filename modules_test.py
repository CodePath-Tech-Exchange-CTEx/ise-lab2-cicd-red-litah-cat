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

# -------------------------
# Helpers 
# -------------------------

def run_display_post(username, user_image, timestamp, content, post_image) -> AppTest:
    """Create a fresh test app session for display_post and run once."""
    at = AppTest.from_string(f"""
import streamlit as st 
import modules

modules.st = st 
st.session_state["rendered_posts"] = [] 

def spy_create_component(data, html_file_name, **kwargs): 
    st.session_state["rendered_posts"].append({{ 
        "data": data, 
        "html_file_name": html_file_name, 
        "kwargs": kwargs, 
    }})

modules.create_component = spy_create_component

modules.display_post( 
    {username!r}, 
    {user_image!r}, 
    {timestamp!r},
    {content!r},
    {post_image!r}, 
)
""", default_timeout=10).run()

    assert not at.exception
    return at


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

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    pass
if __name__ == "__main__":
    unittest.main()
