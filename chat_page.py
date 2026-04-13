import streamlit as st
from data_fetcher import get_chat_history, chat_with_ai, get_fitness_profile, save_fitness_profile, get_user_profile
from modules import display_chat_history, display_ai_trainer_hero

# ── CSS injected once per page load ───────────────────────────────────────────

_PAGE_CSS = """
<style>
/* ── Shared secondary button cleanup ── */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    padding: 0 !important;
    min-height: auto !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: color 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: transparent !important;
    border: none !important;
    color: #f97316 !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:focus,
div[data-testid="stButton"] > button[kind="secondary"]:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}

/* ── Subtle back-button ── */
button[kind="secondary"] {
    color: #6b7280 !important;
}

/* ── Profile nav item — single unit matching the navbar tabs ── */
div[data-testid="stVerticalBlock"]:has(.profile-btn-hook) div[data-testid="stButton"] > button {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    padding: 14px 4px 10px !important;
    min-height: 74px !important;
    width: 96px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    transition: color 0.2s ease !important;
    cursor: pointer !important;
}

/* Icon as ::before — same technique as the navbar tabs */
div[data-testid="stVerticalBlock"]:has(.profile-btn-hook) div[data-testid="stButton"] > button::before {
    content: '';
    display: block;
    width: 22px;
    height: 22px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E");
}

/* Hover — both icon and text change to accent together */
div[data-testid="stVerticalBlock"]:has(.profile-btn-hook) div[data-testid="stButton"] > button:hover {
    color: #f97316 !important;
    background: transparent !important;
}

div[data-testid="stVerticalBlock"]:has(.profile-btn-hook) div[data-testid="stButton"] > button:hover::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E");
}

@media (max-width: 768px) {
    div[data-testid="stVerticalBlock"]:has(.profile-btn-hook) div[data-testid="stButton"] > button {
        width: 84px !important;
        font-size: 9px !important;
    }
}
</style>
"""


# ── Profile form (unchanged logic, small visual polish) ───────────────────────

def _display_profile_form(user_id):
    """Renders the fitness profile form. Returns to chat on 'Back'."""
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            st.session_state.show_profile = False
            st.rerun()
    with col_title:
        st.subheader("My Fitness Profile")

    st.markdown("Your profile helps Arnold personalise advice for you.")
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


# ── Profile button rendered with Lucide icon above ────────────────────────────

def _render_profile_button(user_id):
    """Renders an inline profile trigger styled like the main nav icons."""
    profile_col, _ = st.columns([1, 6])
    with profile_col:
        st.markdown('<div class="profile-btn-hook"></div>', unsafe_allow_html=True)
        if st.button("PROFILE", key="profile_btn"):
            st.session_state.show_profile = True
            st.rerun()


# ── Main page ─────────────────────────────────────────────────────────────────

def display_chat_page(user_id):
    # Inject page-level CSS once
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    # Initialise session state
    if "show_profile" not in st.session_state:
        st.session_state.show_profile = False

    # ── Profile view ──
    if st.session_state.show_profile:
        _display_profile_form(user_id)
        return

    # ── Resolve display name for greeting ──
    fitness_profile = get_fitness_profile(user_id)
    if fitness_profile and fitness_profile.get("first_name"):
        display_name = fitness_profile["first_name"]
    else:
        user_profile = get_user_profile(user_id)
        display_name = user_profile.get("full_name", "there")

    # ── Chat history ──
    history = get_chat_history(user_id)

    # ── Hero greeting for empty state ──
    if not history:
        display_ai_trainer_hero(display_name)

    # ── Persistent chat input (Streamlit pins this to the bottom) ──
    prompt = st.chat_input("Ask Arnold anything related to training...")
    if prompt:
        with st.spinner("Arnold is thinking..."):
            try:
                chat_with_ai(user_id, prompt)
            except Exception as e:
                st.error(f"Error communicating with Arnold: {e}")
        st.rerun()

    # ── Conversation history ──
    if history:
        display_chat_history(history)

    # ── Persistent profile trigger ──
    _render_profile_button(user_id)
