import streamlit as st
from data_fetcher import get_chat_history, chat_with_ai, get_fitness_profile
from modules import display_chat_history

def display_chat_page(user_id):
    st.header("Coach AI Chat")
    st.markdown("Ask me about your workouts, stats, or for general fitness advice!")

    # Remind the user to fill out their profile if they haven't yet.
    profile = get_fitness_profile(user_id)
    if not profile:
        st.info("Complete your **Profile** tab so Coach AI can give personalised advice based on your goals and fitness level.")

    # Persistent chat input pinned at the bottom
    prompt = st.chat_input("Message Coach AI...")
    if prompt:
        with st.spinner("Coach AI is typing..."):
            try:
                # Saves user message, calls Vertex AI, saves model response — all in one call
                chat_with_ai(user_id, prompt)
            except Exception as e:
                st.error(f"Error communicating with AI: {e}")
        st.rerun()

    # Load full history from BigQuery and render as a single component
    history = get_chat_history(user_id)
    if not history:
        st.info("No messages yet. Send a message to start chatting!")
    else:
        display_chat_history(history)
