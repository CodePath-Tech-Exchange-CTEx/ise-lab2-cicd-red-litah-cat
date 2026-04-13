#############################################################################
# profile_page.py
#
# Displays and saves the user's fitness profile.
# Profile data is persisted to BigQuery and used as context by the AI trainer.
#############################################################################

import streamlit as st
from internals import inject_streamlit_global_styles
from data_fetcher import get_fitness_profile, save_fitness_profile


def _label(text, required=False):
    """Render a styled field label with an optional red asterisk."""
    asterisk = '<span class="required">*</span>' if required else ""
    st.markdown(
        f'<span class="pf-label">{text}{asterisk}</span>',
        unsafe_allow_html=True,
    )


def display_profile_page(user_id):
    inject_streamlit_global_styles()

    st.header("My Profile")
    st.markdown(
        "Fill out your profile so your AI trainer can personalise advice for you."
    )

    # Load any previously saved profile to pre-fill the form.
    saved = get_fitness_profile(user_id) or {}

    with st.form("fitness_profile_form"):

        # --- Row 1: First name | Last name ---
        col1, col2 = st.columns(2)
        with col1:
            _label("First name", required=True)
            first_name = st.text_input(
                "First name",
                value=saved.get("first_name", ""),
                placeholder="Emma",
                label_visibility="collapsed",
            )
        with col2:
            _label("Last name")
            last_name = st.text_input(
                "Last name",
                value=saved.get("last_name", ""),
                placeholder="Crown",
                label_visibility="collapsed",
            )

        # --- Row 2: Age | Sex ---
        col3, col4 = st.columns(2)
        with col3:
            _label("Age", required=True)
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                step=1,
                value=int(saved.get("age") or 0),
                label_visibility="collapsed",
            )
        with col4:
            sex_options = ["", "Male", "Female", "Non-binary", "Prefer not to say"]
            saved_sex = saved.get("sex", "")
            sex_index = sex_options.index(saved_sex) if saved_sex in sex_options else 0
            _label("Sex")
            sex = st.selectbox(
                "Sex",
                sex_options,
                index=sex_index,
                label_visibility="collapsed",
            )

        # --- Row 3: Height | Weight ---
        col5, col6 = st.columns(2)
        with col5:
            _label("Height")
            height = st.text_input(
                "Height",
                value=saved.get("height", ""),
                placeholder="e.g. 5'10\" or 178 cm",
                label_visibility="collapsed",
            )
        with col6:
            _label("Weight")
            weight = st.text_input(
                "Weight",
                value=saved.get("weight", ""),
                placeholder="e.g. 165 lbs or 75 kg",
                label_visibility="collapsed",
            )

        # --- Row 4: Fitness Level ---
        fitness_level_options = ["", "Beginner", "Intermediate", "Advanced"]
        saved_level = saved.get("fitness_level", "")
        level_index = (
            fitness_level_options.index(saved_level)
            if saved_level in fitness_level_options
            else 0
        )
        _label("Fitness level")
        fitness_level = st.selectbox(
            "Fitness Level",
            fitness_level_options,
            index=level_index,
            label_visibility="collapsed",
        )

        # --- Injuries / Limitations ---
        _label("Injuries / Limitations")
        injuries_limitations = st.text_area(
            "Injuries / Limitations",
            value=saved.get("injuries_limitations", ""),
            placeholder="Describe any injuries or physical limitations (or leave blank)",
            label_visibility="collapsed",
        )

        # --- Section divider + Goal cards ---
        st.markdown('<hr class="pf-divider">', unsafe_allow_html=True)
        st.markdown(
            '<div class="pf-section-title">Select a primary goal</div>',
            unsafe_allow_html=True,
        )

        goal_options = ["Lose Weight", "Build Muscle", "Flexibility"]
        saved_goal = saved.get("primary_goal", "Lose Weight")
        if saved_goal not in goal_options:
            saved_goal = "Lose Weight"

        primary_goal = st.radio(
            "Primary Goal",
            goal_options,
            index=goal_options.index(saved_goal),
            horizontal=True,
            label_visibility="collapsed",
        )

        # --- Buttons ---
        st.markdown('<hr class="pf-divider">', unsafe_allow_html=True)
        _, col_submit = st.columns([3, 1])
        with col_submit:
            submitted = st.form_submit_button(
                "Save Profile", type="secondary", use_container_width=True
            )

    if submitted:
        if not first_name or not last_name:
            st.error("Please enter at least your first and last name.")
        else:
            try:
                save_fitness_profile(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    sex=sex,
                    height=height,
                    weight=weight,
                    fitness_level=fitness_level,
                    injuries_limitations=injuries_limitations,
                    primary_goal=primary_goal,
                )
                st.success(
                    "Profile saved! Your AI trainer will now use this to personalise your advice."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Could not save profile: {e}")