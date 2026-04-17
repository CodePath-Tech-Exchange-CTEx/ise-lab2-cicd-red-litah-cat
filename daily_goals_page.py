import streamlit as st
from datetime import datetime
from modules import display_goals
from data_fetcher import get_daily_goals, get_user_profile, update_goal_status

def load_workout_css():
    with open("CSS/daily_goals.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def display_workout_header(go_to):
    user_profile = get_user_profile(user_id)
    profile_image = user_profile["profile_image"]

    left, middle, right = st.columns([1, 5, 1])

    with left:
        st.markdown('<div class="home-button-wrap">', unsafe_allow_html=True)
        if st.button("⌂", key="workout_home_button"):
            go_to("home")
        st.markdown('</div>', unsafe_allow_html=True)

    with middle:
        st.markdown(
            f'<div class="workout-title">{datetime.now().strftime("%A, %d %B")}</div>',
            unsafe_allow_html=True
        )

    with right:
        st.image(profile_image, width=60)

    st.divider()


def display_goals_page():
    load_workout_css()
    display_workout_header(go_to)

    st.markdown(
        '<div class="section-label">View your daily goals:</div>',
        unsafe_allow_html=True
    )

    goals = get_daily_goals(user_id)

    if not goals:
        st.write("No goals for today yet.")
        return

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

    st.markdown('<div class="add-goal-label">Add new goal</div>', unsafe_allow_html=True)
    left, center, right = st.columns([3.6, 1, 3])
    with center:
        if st.button("✚", key="open_add_goal_modal"):
            st.session_state.show_add_goal_modal = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_add_goal_modal:
        display_add_goal_modal()
        st.session_state.show_add_goal_modal = False
