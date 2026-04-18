#############################################################################
# workout_plan_page.py
#
# This file contains the Workout Plans page for viewing saved plans and
# opening workout detail popups.
#############################################################################

import streamlit as st
from data_fetcher import get_user_workout_plans


def _render_workout_plan_card(plan, button_key):
    """Render a small plan card with a Start Workout button."""
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"#### {plan['name']}")
        st.markdown(f"**Duration:** {plan['duration']} minutes")
        st.markdown(f"**Goal:** {plan['goal']}")
    with col2:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        st.markdown("&nbsp;", unsafe_allow_html=True)
        st.markdown(f"**{plan['workout_count']} exercises**")
    with col3:
        if st.button("Start Workout", key=button_key):
            st.session_state['selected_workout_plan'] = plan['plan_id']


def _show_workout_details(plan):
    """Show a modal or fallback expander with the exercise breakdown."""
    if hasattr(st, 'modal'):
        context = st.modal(plan['name'])
    else:
        context = st.expander(plan['name'])

    with context:
        st.markdown(f"### {plan['name']}")
        st.markdown(f"**Duration:** {plan['duration']} minutes")
        st.markdown(f"**Goal:** {plan['goal']}")
        st.markdown("---")
        st.markdown("### Exercise Breakdown")
        for exercise in plan['exercises']:
            sets_reps = exercise.get('sets_reps', '')
            duration = exercise.get('duration', '')
            rest = exercise.get('rest', '')
            exercise_details = f"**{exercise['name']}**"
            if sets_reps:
                exercise_details += f" • {sets_reps}"
            if duration:
                exercise_details += f" • {duration}"
            if rest:
                exercise_details += f" • Rest {rest}"
            st.markdown(exercise_details)
            if exercise.get('notes'):
                st.markdown(f"_{exercise['notes']}_")
        st.markdown("---")
        if st.button("Begin Workout", key=f"begin_{plan['plan_id']}"):
            st.success(f"Ready to start {plan['name']}!")
        if st.button("Close", key=f"close_{plan['plan_id']}"):
            st.session_state.pop('selected_workout_plan', None)


def display_workout_plan_page():
    """Displays the workout plans page with saved plans and detail popups."""
    st.header("Workout Plans")
    st.markdown(
        "Explore your saved workout plans and open a plan to view the full exercise breakdown. "
        "Tap Start Workout to open the detail popup."
    )

    workout_plans = get_user_workout_plans('user1')

    if not workout_plans:
        st.info("You have no saved workout plans yet.")
        return

    for plan in workout_plans:
        _render_workout_plan_card(plan, button_key=f"start_{plan['plan_id']}")
        st.divider()

    selected_plan_id = st.session_state.get('selected_workout_plan')
    if selected_plan_id:
        selected_plan = next(
            (plan for plan in workout_plans if plan['plan_id'] == selected_plan_id),
            None,
        )
        if selected_plan:
            _show_workout_details(selected_plan)
        else:
            st.session_state.pop('selected_workout_plan', None)


if __name__ == '__main__':
    display_workout_plan_page()
