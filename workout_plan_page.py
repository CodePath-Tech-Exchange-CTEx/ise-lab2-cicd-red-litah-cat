#############################################################################
# workout_plan_page.py
#
# This file contains the Workout Plan page for recording workout sessions.
#############################################################################

import streamlit as st
from datetime import datetime, date
from modules import display_workout_plan_card
from data_fetcher import get_logged_workouts, save_logged_workout

user_id = "user1"


def load_workout_plan_css():
    with open("custom_components/workout_plan.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def display_workout_plan_header():
    left, middle, right = st.columns([1, 5, 1])

    with middle:
        st.markdown(
            f'<div class="workout-title">{datetime.now().strftime("%A, %d %B")}</div>',
            unsafe_allow_html=True
        )

    st.divider()


@st.dialog(" ")
def display_add_workout_plan_modal():
    st.markdown('<div class="custom-modal-title">Add New Workout Plan</div>', unsafe_allow_html=True)

    st.markdown('<div class="modal-field-label">Workout Type</div>', unsafe_allow_html=True)
    workout_type = st.selectbox(
        label="Workout Type",
        label_visibility="collapsed",
        options=["Running", "Cycling", "Strength Training", "Swimming",
                 "Yoga", "HIIT", "Walking", "Other"],
        key="new_workout_type"
    )

    st.markdown('<div class="modal-field-label">Duration (minutes)</div>', unsafe_allow_html=True)
    duration_text = st.text_input(
        label="Duration",
        label_visibility="collapsed",
        placeholder="e.g. 30",
        key="new_workout_duration"
    )

    st.markdown('<div class="modal-field-label">Intensity</div>', unsafe_allow_html=True)
    intensity = st.select_slider(
        label="Intensity",
        label_visibility="collapsed",
        options=["Low", "Moderate", "High", "Max"],
        value="Moderate",
        key="new_workout_intensity"
    )

    st.markdown('<div class="modal-field-label">Calories Burned (optional)</div>', unsafe_allow_html=True)
    calories_text = st.text_input(
        label="Calories",
        label_visibility="collapsed",
        placeholder="e.g. 250",
        key="new_workout_calories"
    )

    st.markdown('<div class="modal-field-label">Date</div>', unsafe_allow_html=True)
    workout_date = st.date_input(
        label="Date",
        label_visibility="collapsed",
        value=date.today(),
        key="new_workout_date"
    )

    st.markdown('<div class="modal-field-label">Notes (optional)</div>', unsafe_allow_html=True)
    notes = st.text_area(
        label="Notes",
        label_visibility="collapsed",
        placeholder="How did it go?",
        key="new_workout_notes"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="cancel_workout_plan", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Save", key="save_workout_plan", type="primary", use_container_width=True):
            clean_duration = duration_text.strip()

            if clean_duration == "":
                st.warning("Please enter a duration.")
                return

            if not clean_duration.isdigit():
                st.warning("Duration must be a whole number in minutes.")
                return

            duration = int(clean_duration)

            if duration <= 0:
                st.warning("Duration must be greater than 0.")
                return

            calories = 0
            if calories_text.strip():
                if not calories_text.strip().isdigit():
                    st.warning("Calories must be a whole number.")
                    return
                calories = int(calories_text.strip())

            save_logged_workout(user_id, workout_type, duration, intensity,
                                calories, workout_date, notes)
            st.rerun()


def display_workout_plan_page():
    """Displays the Workout Plan page with a card-based list and an add modal."""
    load_workout_plan_css()

    st.markdown('<div class="daily-goals-page">', unsafe_allow_html=True)

    display_workout_plan_header()

    st.markdown(
        '<div class="section-label">View your workout plans:</div>',
        unsafe_allow_html=True
    )

    workouts = get_logged_workouts(user_id)

    if not workouts:
        st.write("No workout plans added yet.")
    else:
        for workout in workouts:
            left_space, card_col, right_space = st.columns([2.1, 6.8, 1.1])

            with card_col:
                display_workout_plan_card(
                    workout["workout_type"],
                    workout["duration"],
                    workout["intensity"],
                    workout["workout_date"]
                )

    workout_plan_cta = st.container(key="workout_plan_cta")
    with workout_plan_cta:
        st.markdown('<div class="add-goal-label">Add new workout plan</div>', unsafe_allow_html=True)
        if st.button("✚", key="open_workout_plan_modal"):
            display_add_workout_plan_modal()

    st.markdown('</div>', unsafe_allow_html=True)
