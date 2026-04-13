#############################################################################
# profile_page.py
#
# Displays and saves the user's fitness profile.
# Profile data is persisted to BigQuery and used as context by the AI trainer.
#############################################################################

import streamlit as st
from data_fetcher import get_fitness_profile, save_fitness_profile


def _inject_profile_styles():
    st.markdown("""
    <style>
    /* ============================================================
       PROFILE PAGE — DARK THEME
    ============================================================ */

    /* ---------- Custom field labels ---------- */
    .pf-label {
        color: #e8e8e8;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 4px;
        display: block;
    }
    .pf-label .required {
        color: #f04c4c;
        margin-left: 2px;
    }

    /* ---------- Text / Number inputs ---------- */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background-color: #1c1c1c !important;
        border: 1px solid #383838 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        transition: border-color 0.15s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: #666 !important;
        box-shadow: none !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder {
        color: #555 !important;
    }

    /* ---------- Text area ---------- */
    [data-testid="stTextArea"] textarea {
        background-color: #1c1c1c !important;
        border: 1px solid #383838 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        font-size: 14px !important;
        transition: border-color 0.15s ease !important;
    }
    [data-testid="stTextArea"] textarea:focus {
        border-color: #666 !important;
        box-shadow: none !important;
    }
    [data-testid="stTextArea"] textarea::placeholder {
        color: #555 !important;
    }

    /* ---------- Selectbox ---------- */
    [data-testid="stSelectbox"] > div > div {
        background-color: #1c1c1c !important;
        border: 1px solid #383838 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
    }
    [data-testid="stSelectbox"] svg {
        fill: #888 !important;
    }

    /* ---------- Hide native Streamlit widget labels (we render our own) ---------- */
    [data-testid="stTextInput"]  > label,
    [data-testid="stNumberInput"] > label,
    [data-testid="stTextArea"]   > label,
    [data-testid="stSelectbox"]  > label {
        display: none !important;
    }

    /* ---------- Remove default form border ---------- */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* ---------- Section divider ---------- */
    .pf-divider {
        border: none;
        border-top: 1px solid #2e2e2e;
        margin: 24px 0;
    }

    /* ---------- Section title ---------- */
    .pf-section-title {
        color: #e8e8e8;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 16px;
    }

    /* ---------- Goal cards — style the horizontal radio as cards ---------- */

    /* Outer radio container: remove default label */
    [data-testid="stRadio"] > div > div:first-child {
        display: none !important;
    }

    /* Make the options flex horizontally (already horizontal=True, reinforced here) */
    [data-testid="stRadio"] [role="radiogroup"],
    [data-testid="stRadio"] > div > div:last-child > div {
        display: flex !important;
        flex-direction: row !important;
        gap: 12px !important;
        width: 100% !important;
    }

    /* Each option wrapper stretches equally */
    [data-testid="stRadio"] [role="radiogroup"] > div,
    [data-testid="stRadio"] > div > div:last-child > div > div {
        flex: 1 !important;
    }

    /* Card-style label */
    [data-testid="stRadio"] label {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 8px !important;
        background: #1c1c1c !important;
        border: 1.5px solid #383838 !important;
        border-radius: 10px !important;
        padding: 16px !important;
        cursor: pointer !important;
        width: 100% !important;
        transition: border-color 0.15s ease !important;
    }
    [data-testid="stRadio"] label:hover {
        border-color: #555 !important;
    }

    /* Selected card: white border */
    [data-testid="stRadio"] label:has(input[type="radio"]:checked) {
        border-color: #ffffff !important;
        background: #232323 !important;
    }

    /* Radio circle: reposition to top-right */
    [data-testid="stRadio"] label > div:first-child {
        order: 3 !important;
        margin-left: auto !important;
        align-self: flex-start !important;
    }

    /* Goal name text */
    [data-testid="stRadio"] label > div:last-child,
    [data-testid="stRadio"] label > p {
        order: 1 !important;
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    /* ---------- Submit button ---------- */
    [data-testid="stFormSubmitButton"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #e0e0e0 !important;
    }

    /* ---------- "Go back" secondary button ---------- */
    [data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #e8e8e8 !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 24px !important;
        cursor: pointer !important;
        transition: border-color 0.15s ease !important;
    }
    [data-testid="stButton"] > button:hover {
        border-color: #888 !important;
        background-color: #1c1c1c !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _label(text, required=False):
    """Render a styled field label with an optional red asterisk."""
    asterisk = '<span class="required">*</span>' if required else ""
    st.markdown(
        f'<span class="pf-label">{text}{asterisk}</span>',
        unsafe_allow_html=True,
    )


def display_profile_page(user_id):
    _inject_profile_styles()

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
                "Save Profile", use_container_width=True
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
