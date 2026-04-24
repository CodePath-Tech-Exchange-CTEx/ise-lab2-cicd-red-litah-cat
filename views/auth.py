import streamlit as st
import re
from backend.data_fetcher import verify_login, create_new_user

def is_valid_username(username):
    """
    Returns True if the username contains ONLY letters, numbers, and underscores.
    This naturally blocks spaces, quotes, brackets, and SQL/HTML injection characters.
    """
    return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

def display_auth_page():
    # We use columns to center the login box on the screen and make it sleek
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown("<h2 style='text-align: center;'>Welcome</h2>", unsafe_allow_html=True)
        
        # Using tabs creates a clean, professional toggle without taking up vertical space
        login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])
        
        # --- LOGIN TAB ---
        with login_tab:
            # Using st.form ensures users can just press "Enter" to submit
            with st.form("login_form"):
                login_user = st.text_input("Username")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Log In", use_container_width=True)
                
                if submit_login:
                    if not login_user or not login_pass:
                        st.error("Please fill in all fields.")
                    else:
                        user_id = verify_login(login_user, login_pass)
                        if user_id:
                            st.session_state.logged_in = True
                            st.session_state.current_user_id = user_id
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                            
        # --- SIGN UP TAB ---
        with signup_tab:
            with st.form("signup_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name")
                with col2:
                    last_name = st.text_input("Last Name")
                    
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit_signup:
                    # Form Validation Check
                    if not first_name or not last_name or not new_user or not new_pass or not confirm_pass:
                        st.error("Please fill in all fields.")
                    elif not is_valid_username(new_user):
                        st.error("Username can only contain letters, numbers, and underscores.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        new_user_id = create_new_user(first_name, last_name, new_user, new_pass)
                        if new_user_id:
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error("That username is already taken. Please choose another.")