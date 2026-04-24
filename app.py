#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from utils.modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from backend.data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from views.activity_page import display_activity_page
from views.community_page import display_community_page
from views.daily_goals_page import display_daily_goals_page
from views.chat_page import display_chat_page
from views.workout_plan_page import display_workout_plan_page
import datetime

from views.auth import display_auth_page

# --- INITIALIZE SESSION STATE ---
# This runs once when the user first visits the URL
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None


def display_app_page(userId):
    # # Pull the ID dynamically from the logged-in user
    # userId = st.session_state.current_user_id 
    
    st.header("Posts")

    # --- Post logic --- (hardcoded because there's no create post feature)
    user_profile = get_user_profile(userId)
    username = user_profile['username']
    user_image = user_profile['profile_image']
    
    post = get_user_posts(userId)
    if post:
        timestamp = post[0]['timestamp']
        content = post[0]['content']
        post_image = post[0]['image']
    
        display_post(username, user_image, timestamp, content, post_image)
    else:
        st.info("No posts yet. Create a workout in the Workout Plan tab and share it in the Activity tab!")
    
    # --- Activity Summary Logic ---
    st.header("Activity Summary")
    
    user_workouts = get_user_workouts(userId)
    display_activity_summary(user_workouts)
    
    # --- Recent Workouts Logic ---
    st.header("Recent Activity")
    
    display_recent_workouts(user_workouts)
    
    # --- GenAI Logic ---
    st.markdown("## 🤖 AI Advice")
    
    gen_ai_advice = get_genai_advice(userId)
    timestamp = gen_ai_advice['timestamp']
    content = gen_ai_advice['content']
    image = gen_ai_advice['image']
    
    display_genai_advice(timestamp, content, image)

 
# This is the starting point for your app.
if __name__ == '__main__':
    with open('components/streamlit_global.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # --- THE ROUTER ---
    if not st.session_state.logged_in:
        # If they aren't logged in, ONLY show the login/signup screen
        display_auth_page()
        
    else:
        # If they are logged in, load the main app layout
        userId = st.session_state.current_user_id
        
        home_tab, activity_tab, workout_plan_tab, daily_goals_tab, ai_trainer_tab, community_tab = st.tabs(
            ["Home", "Activity", "Workout Plan", "Daily Goals", "AI Trainer", "Community"]
        )

        with home_tab:
            display_app_page(userId)

        with activity_tab:
            display_activity_page(userId)

        with workout_plan_tab:
            display_workout_plan_page(userId)

        with daily_goals_tab:
            display_daily_goals_page(userId)
            
        with ai_trainer_tab:
            display_chat_page(userId)

        with community_tab:
            display_community_page(userId)