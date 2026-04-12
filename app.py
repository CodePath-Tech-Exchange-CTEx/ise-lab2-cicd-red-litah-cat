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
 
 
def inject_navbar_styles():
    st.markdown("""
    <style>
    /* ===== CUSTOM NAVIGATION BAR ===== */

    /* Tab container */
    [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: none !important;
        padding: 0 !important;
        gap: 0 !important;
        justify-content: space-around !important;
    }

    /* Individual tab buttons */
    [data-baseweb="tab"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 14px 4px 10px !important;
        color: #ffffff !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        background: transparent !important;
        gap: 6px !important;
        min-height: 74px !important;
        text-transform: uppercase !important;
        transition: color 0.2s ease !important;
    }

    /* Hover state */
    [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: transparent !important;
    }

    /* Active tab */
    [aria-selected="true"][data-baseweb="tab"] {
        color: #f97316 !important;
        background: transparent !important;
    }

    /* Active underline indicator */
    [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Hide default tab border */
    [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Tab label text */
    [data-baseweb="tab"] p {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Icon base styles via ::before pseudo-elements */
    [data-baseweb="tab"]::before {
        content: '';
        display: block;
        width: 22px;
        height: 22px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.95;
        transition: opacity 0.2s ease;
        flex-shrink: 0;
    }

    [aria-selected="true"][data-baseweb="tab"]::before {
        opacity: 1;
        filter: none !important;
    }

    /* Home icon — house */
    [data-baseweb="tab"]:nth-child(1)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3Cpolyline points='9 22 9 12 15 12 15 22'/%3E%3C/svg%3E");
    }

    /* Activity icon — pulse/activity */
    [data-baseweb="tab"]:nth-child(2)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='22 12 18 12 15 21 9 3 6 12 2 12'/%3E%3C/svg%3E");
    }

    /* Log Workout icon — circle-plus */
    [data-baseweb="tab"]:nth-child(3)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 8v8'/%3E%3Cpath d='M8 12h8'/%3E%3C/svg%3E");
    }

    /* AI Trainer icon — bot */
    [data-baseweb="tab"]:nth-child(4)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 8V4H8'/%3E%3Crect width='16' height='12' x='4' y='8' rx='2'/%3E%3Cpath d='M2 14h2'/%3E%3Cpath d='M20 14h2'/%3E%3Cpath d='M15 13v2'/%3E%3Cpath d='M9 13v2'/%3E%3C/svg%3E");
    }

    /* Community icon — users */
    [data-baseweb="tab"]:nth-child(5)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3Cpath d='M23 21v-2a4 4 0 0 0-3-3.87'/%3E%3Cpath d='M16 3.13a4 4 0 0 1 0 7.75'/%3E%3C/svg%3E");
    }
    </style>
    """, unsafe_allow_html=True)


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    inject_navbar_styles()

    home_tab, activity_tab, log_workout_tab, ai_trainer_tab, community_tab = st.tabs(
        ["Home", "Activity", "Log Workout", "AI Trainer", "Community"]
    )

    with home_tab:
        display_app_page()

    with activity_tab:
        display_activity_page()

    with log_workout_tab:
        display_log_workout_page()

    with ai_trainer_tab:
        display_chat_page(userId)

    with community_tab:
        display_community_page()
