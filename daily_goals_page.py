import streamlit as st
from datetime import datetime
from modules import display_goals
from data_fetcher import get_daily_goals, get_user_profile, update_goal_status, save_new_goal


def load_workout_css():
    with open("custom_components/daily_goals.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def display_workout_header(userId):
    user_profile = get_user_profile(userId)
    profile_image = user_profile["profile_image"]

    left, middle, right = st.columns([1, 5, 1])

    with middle:
        st.markdown(
            f'<div class="workout-title">{datetime.now().strftime("%A, %d %B")}</div>',
            unsafe_allow_html=True
        )

    with right:
        if profile_image:
            st.image(profile_image, width=60)
        else:
            # Use a default generic avatar silhouette if they don't have one
            DEFAULT_AVATAR = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
            st.image(DEFAULT_AVATAR, width=60)

    st.divider()


@st.dialog(" ")
def display_add_goal_modal(userId):
    st.markdown('<div class="custom-modal-title">Add New Goal</div>', unsafe_allow_html=True)

    st.markdown('<div class="modal-field-label">Goal Name</div>', unsafe_allow_html=True)
    goal_name = st.text_input(
        label="Goal Name",
        label_visibility="collapsed",
        placeholder="e.g Push-ups, Running",
        key="new_goal_name"
    )

    st.markdown('<div class="modal-field-label">Duration (minutes)</div>', unsafe_allow_html=True)
    duration_text = st.text_input(
        label="Duration (minutes)",
        label_visibility="collapsed",
        placeholder="e.g 20",
        key="new_goal_duration"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="cancel_add_goal", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Save", key="save_add_goal", type="primary", use_container_width=True):
            clean_name = goal_name.strip()
            clean_duration = duration_text.strip()

            if clean_name == "":
                st.warning("Please enter a goal name.")
                return

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

            save_new_goal(userId, clean_name, duration)
            st.rerun()


def display_daily_goals_page(userId):
    load_workout_css()

    st.markdown('<div class="daily-goals-page">', unsafe_allow_html=True)

    display_workout_header(userId)

    st.markdown(
        '<div class="section-label">View your daily goals:</div>',
        unsafe_allow_html=True
    )

    goals = get_daily_goals(userId)

    if not goals:
        st.write("No goals for today yet.")
    else:
        for goal in goals:
            left_space, card_col, check_col, right_space = st.columns([2.1, 5.4, 1.4, 1.1])

            with card_col:
                display_goals(
                    goal["goal_name"],
                    goal["duration"],
                    goal["status"]
                )

            with check_col:
                new_status = st.checkbox(
                    "Done?",
                    value=goal["status"],
                    key=f"daily_goal_{goal['goal_id']}"
                )

                if new_status != goal["status"]:
                    update_goal_status(goal["goal_id"], new_status)
                    st.rerun()

    add_goal_cta = st.container(key="add_goal_cta")
    with add_goal_cta:
        st.markdown('<div class="add-goal-label">Add new goal</div>', unsafe_allow_html=True)

        spacer_left, center_col, spacer_right = st.columns([4, 1, 4])

        with center_col:
            if st.button("✚", key="open_add_goal_modal"):
                display_add_goal_modal(userId)

    st.markdown('</div>', unsafe_allow_html=True)