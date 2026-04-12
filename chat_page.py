import streamlit as st
from data_fetcher import get_chat_history, chat_with_ai, get_fitness_profile, save_fitness_profile
from modules import display_chat_history


def _display_profile_form(user_id):
    """Renders the profile form inline. Returns True if the user pressed Back."""

    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Back to Chat"):
            st.session_state.show_profile = False
            st.rerun()
    with col_title:
        st.subheader("My Profile")

    st.markdown("Your profile helps Coach AI personalise advice for you.")
    st.divider()

    saved = get_fitness_profile(user_id) or {}

    with st.form("fitness_profile_form_inline"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", value=saved.get("first_name", ""))
        with col2:
            last_name = st.text_input("Last Name", value=saved.get("last_name", ""))

        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input(
                "Age", min_value=0, max_value=120, step=1,
                value=int(saved.get("age") or 0)
            )
        with col4:
            sex_options = ["", "Male", "Female", "Non-binary", "Prefer not to say"]
            saved_sex = saved.get("sex", "")
            sex_index = sex_options.index(saved_sex) if saved_sex in sex_options else 0
            sex = st.selectbox("Sex", sex_options, index=sex_index)

        col5, col6 = st.columns(2)
        with col5:
            height = st.text_input(
                "Height (e.g. 5'10\" or 178 cm)",
                value=saved.get("height", "")
            )
        with col6:
            weight = st.text_input(
                "Weight (e.g. 165 lbs or 75 kg)",
                value=saved.get("weight", "")
            )

        level_options = ["", "Beginner", "Intermediate", "Advanced"]
        saved_level = saved.get("fitness_level", "")
        level_index = level_options.index(saved_level) if saved_level in level_options else 0
        fitness_level = st.selectbox("Fitness Level", level_options, index=level_index)

        injuries = st.text_area(
            "Injuries / Limitations",
            value=saved.get("injuries_limitations", ""),
            placeholder="Describe any injuries or limitations (or leave blank)"
        )

        st.markdown("**Primary Goal**")
        goal_options = ["Lose Weight", "Build Muscle", "Flexibility"]
        saved_goal = saved.get("primary_goal", "Lose Weight")
        if saved_goal not in goal_options:
            saved_goal = "Lose Weight"
        primary_goal = st.radio(
            "Primary Goal",
            goal_options,
            index=goal_options.index(saved_goal),
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button("Save Profile")

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
                    injuries_limitations=injuries,
                    primary_goal=primary_goal,
                )
                st.success("Profile saved! Returning to chat...")
                st.session_state.show_profile = False
                st.rerun()
            except Exception as e:
                st.error(f"Could not save profile: {e}")


def display_chat_page(user_id):
    # Initialise session state for profile view toggle.
    if "show_profile" not in st.session_state:
        st.session_state.show_profile = False

    # --- Profile view ---
    if st.session_state.show_profile:
        _display_profile_form(user_id)
        return

    # --- Chat view ---
    # Header row: title on left, profile button on right.
    col_title, col_profile_btn = st.columns([5, 1])
    with col_title:
        st.header("Coach AI")
    with col_profile_btn:
        # Vertical spacer to align button with header.
        st.write("")
        profile = get_fitness_profile(user_id)
        btn_label = "👤 Profile" if profile else "👤 Set up profile"
        if st.button(btn_label, use_container_width=True):
            st.session_state.show_profile = True
            st.rerun()

    if not profile:
        st.caption("Complete your profile so Coach AI can give personalised advice.")

    # Persistent chat input pinned to bottom by Streamlit automatically.
    prompt = st.chat_input("Message Coach AI...")
    if prompt:
        with st.spinner("Coach AI is typing..."):
            try:
                chat_with_ai(user_id, prompt)
            except Exception as e:
                st.error(f"Error communicating with AI: {e}")
        st.rerun()

    # Render the conversation history.
    history = get_chat_history(user_id)
    if not history:
        st.markdown(
            "<p style='color:#6b7280; font-size:0.9em;'>No messages yet — send one below to start.</p>",
            unsafe_allow_html=True,
        )
    else:
        display_chat_history(history)
