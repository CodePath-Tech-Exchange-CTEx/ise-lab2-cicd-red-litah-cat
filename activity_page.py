#############################################################################
# activity_page.py
#
# This file contains the activity page of the app. It displays a user's
# recent workouts, activity summary, and a button to share a stat as a post.
#############################################################################

import streamlit as st
from modules import display_recent_workouts, display_activity_summary
from data_fetcher import get_user_workouts, insert_post


def display_activity_page(userId):
    """Displays the activity page, including recent workouts, an activity
    summary, and a button to share a workout stat with the community."""

    user_workouts = get_user_workouts(userId)
    recent_workouts = user_workouts[:3]

    # --- Activity Summary ---
    st.subheader("Activity Summary")
    display_activity_summary(user_workouts)

    # --- Recent Workouts ---
    st.divider()
    st.subheader("Recent Workouts")
    display_recent_workouts(recent_workouts)

    # --- Share Button ---
    st.divider()
    with st.form("share_activity_form"):
        submitted = st.form_submit_button("Share My Activity")
    if submitted:
        if recent_workouts:
            latest = recent_workouts[0]
            workout_duration = latest.get('duration_minutes')
            calories_burned = latest.get('calories_burned')
            
            if calories_burned:
                insert_post(userId, f"I worked out for {workout_duration} minutes and burned {calories_burned} calories today!")
                st.success(f"Shared: I worked out for {workout_duration} minutes and burned {calories_burned} calories today!")
            else:
                insert_post(userId, f"I worked out for {workout_duration} minutes and burned a lot of calories today!")
                st.success(f"Shared: I worked out for {workout_duration} minutes and burned a lot of calories today!")
        else:
            st.warning("No workouts to share yet.")


if __name__ == '__main__':
    display_activity_page()