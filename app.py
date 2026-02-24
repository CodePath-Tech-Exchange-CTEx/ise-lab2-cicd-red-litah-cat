#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'

def display_app_page():
    """Displays the home page of the app."""

    # --- Post logic ---
    user_profile = get_user_profile(userId)
    username = user_profile['username']
    user_image = user_profile['profile_image']

    post = get_user_posts(userId)
    timestamp = post[0]['timestamp']
    content = post[0]['content']
    post_image = post[0]['image']

    display_post(username, user_image, timestamp, content, post_image)

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
