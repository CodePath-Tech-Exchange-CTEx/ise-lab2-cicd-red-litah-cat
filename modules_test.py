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

# -------------------------
# Helpers 
# -------------------------

def run_display_post(username, user_image, timestamp, content, post_image) -> AppTest:
    """Create a fresh test app session for display_post and run once."""
    at = AppTest.from_string(f"""
import streamlit as st 
import modules

modules.st = st 
st.session_state["rendered_posts"] = [] #Line written by ChatGPT

def spy_create_component(data, html_file_name, **kwargs): #Line written by ChatGPT
    st.session_state["rendered_posts"].append({{ #Line written by ChatGPT
        "data": data, #Line written by ChatGPT
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

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
