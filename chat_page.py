import streamlit as st
from data_fetcher import get_chat_history, chat_with_ai, get_fitness_profile, save_fitness_profile, get_user_profile
from modules import display_chat_history, display_ai_trainer_hero


# ── Lucide SVG snippets used across the page ──────────────────────────────────

_ICON_USER = """
<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"
     stroke="#f97316" stroke-width="1.6"
     stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="4"/>
  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
</svg>
"""

# ── CSS injected once per page load ───────────────────────────────────────────

_PAGE_CSS = """
<style>
/* ── Profile trigger ── */
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

/* ── Chat input bar ── */
div[data-testid="stChatInput"] {
    background: transparent !important;
}

div[data-testid="stChatInput"] > div {
    background: #1a1a1a !important;
    border: 1.5px solid #333333 !important;
    border-radius: 28px !important;
    padding: 12px 14px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.32) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}

div[data-testid="stChatInput"]:focus-within > div {
    border-color: #f97316 !important;
    box-shadow: 0 12px 40px rgba(249, 115, 22, 0.12) !important;
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 1.02rem !important;
    line-height: 1.5 !important;
    min-height: 112px !important;
    padding: 10px 12px !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
}

div[data-testid="stChatInput"] button {
    width: 48px !important;
    height: 48px !important;
    border-radius: 999px !important;
    border: 2px solid #f97316 !important;
    background: transparent !important;
    color: #f97316 !important;
    transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
}

div[data-testid="stChatInput"] button:hover {
    background: rgba(249, 115, 22, 0.12) !important;
    box-shadow: 0 0 14px rgba(249, 115, 22, 0.22) !important;
    transform: translateY(-1px);
}

div[data-testid="stChatInput"] button:disabled {
    opacity: 0.5 !important;
}

/* ── Subtle back-button ── */
button[kind="secondary"] {
    color: #6b7280 !important;
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
    """Renders the profile trigger with a Lucide user icon above the label."""
    col_btn, _ = st.columns([1.4, 5])
    with col_btn:
        fitness_profile = get_fitness_profile(user_id)
        label = "Profile" if fitness_profile else "Set up Profile"

        st.markdown(
            f"""<div style="display:flex;flex-direction:column;align-items:center;gap:6px;margin-top:8px;">
                  <div style="display:flex;justify-content:center;">
                  {_ICON_USER.format(size=32)}
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )
        if st.button(label, key="profile_btn", use_container_width=True):
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

    # ── Hero greeting (shown only when no messages yet) ──
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

    # ── Profile trigger — bottom-left, nav-like text treatment ──
    st.write("")
    _render_profile_button(user_id)
