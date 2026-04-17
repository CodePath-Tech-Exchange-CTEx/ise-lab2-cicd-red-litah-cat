#############################################################################
# log_workout_page.py
#
# This file contains the Log Workout page for recording workout sessions.
#############################################################################

import streamlit as st
import datetime


def display_log_workout_page():
    """Displays a form for logging a workout session."""
    st.header("Log Workout")
    st.markdown("Record and track your workout sessions.")

    with st.form("log_workout_form"):
        workout_type = st.selectbox(
            "Workout Type",
            ["Running", "Cycling", "Strength Training", "Swimming",
             "Yoga", "HIIT", "Walking", "Other"]
        )

        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=600, value=30
            )
        with col2:
            intensity = st.select_slider(
                "Intensity",
                options=["Low", "Moderate", "High", "Max"],
                value="Moderate"
            )

        col3, col4 = st.columns(2)
        with col3:
            calories = st.number_input(
                "Calories Burned (optional)", min_value=0, max_value=5000, value=0
            )
        with col4:
            workout_date = st.date_input("Date", value=datetime.date.today())

        notes = st.text_area(
            "Notes (optional)", placeholder="How did the workout go?"
        )

        submitted = st.form_submit_button("Save Workout", use_container_width=True)

        if submitted:
            st.success(
                f"Workout logged: {duration} min of {workout_type} "
                f"at {intensity} intensity on {workout_date}."
            )
