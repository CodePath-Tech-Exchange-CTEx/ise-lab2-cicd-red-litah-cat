#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from activity_page import display_activity_page
from community_page import display_community_page
from chat_page import display_chat_page
from log_workout_page import display_log_workout_page
from workout_plan_page import display_workout_plan_page
from internals import inject_streamlit_global_styles
import datetime
 
userId = 'user1'
 
def display_app_page():
    st.header("Posts")

    #Displays the home page of the app.
 
    # --- Post logic ---
    user_profile = get_user_profile(userId)
    username = user_profile['username']
    user_image = user_profile['profile_image']
 
    post = get_user_posts(userId)
    timestamp = post[0]['timestamp']
    content = post[0]['content']
    post_image = post[0]['image']
 
    display_post(username, user_image, timestamp, content, post_image)
 
    # --- Activity Summary Logic ---
    st.divider()
    st.header("Activity Summary")
 
    user_workouts = get_user_workouts(userId)
    display_activity_summary(user_workouts)
 
    # --- Recent Workouts Logic ---
    st.divider()
    st.header("Recent Activity")
    
    display_recent_workouts(user_workouts)
 
    # --- GenAI Logic ---
    st.divider()
    st.markdown("## 🤖 AI Advice")
    
    gen_ai_advice = get_genai_advice(userId)
    timestamp = gen_ai_advice['timestamp']
    content = gen_ai_advice['content']
    image = gen_ai_advice['image']
 
    display_genai_advice(timestamp, content, image)
 

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    inject_streamlit_global_styles()

    home_tab, activity_tab, workout_plans_tab, log_workout_tab, ai_trainer_tab, community_tab = st.tabs(
        ["Home", "Activity", "Workout Plans", "Log Workout", "AI Trainer", "Community"]
    )

    with home_tab:
        display_app_page()

    with activity_tab:
        display_activity_page()

    with workout_plans_tab:
        display_workout_plan_page()

    with log_workout_tab:
        display_log_workout_page()

    with ai_trainer_tab:
        display_chat_page(userId)

    with community_tab:
        display_community_page()
