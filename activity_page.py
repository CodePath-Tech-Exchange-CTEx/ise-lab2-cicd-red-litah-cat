#############################################################################
# activity_page.py
#
# This file contains the activity page of the app. It displays a user's
# recent workouts, activity summary, and a button to share a stat as a post.
#############################################################################

import streamlit as st
from modules import display_recent_workouts, display_activity_summary
from data_fetcher import get_user_workouts, insert_post

userId = 'user1'

def display_activity_page():
    """Displays the activity page, including recent workouts, an activity
    summary, and a button to share a workout stat with the community."""

    st.header("My Activity")

    user_workouts = get_user_workouts(userId)
    recent_workouts = user_workouts[:3]

    # --- Activity Summary ---
    st.divider()
    st.subheader("Activity Summary")
    display_activity_summary(user_workouts)

    # --- Recent Workouts ---
    st.divider()
    st.subheader("Recent Workouts")
    display_recent_workouts(recent_workouts)

    # --- Share Button ---
    st.divider()
    if st.button("Share My Activity"):
        if recent_workouts:
            latest = recent_workouts[0]
            steps = latest.get('steps')
            insert_post(userId, f"I walked {steps} steps today!")
            st.success(f"Shared: I walked {steps} steps today!")
        else:
            st.warning("No workouts to share yet.")


if __name__ == '__main__':
    display_activity_page()