#############################################################################
# workout_plan_page.py
#
# This file contains the Workout Plan page for recording workout sessions.
#############################################################################

import streamlit as st
from datetime import datetime, date
from modules import display_workout_plan_card
from data_fetcher import get_logged_workouts, save_logged_workout



def load_workout_plan_css():
    with open("custom_components/workout_plan.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def display_workout_plan_header():
    left, middle, right = st.columns([1, 5, 1])

    with middle:
        st.markdown(
            f'<div class="workout-title">{datetime.now().strftime("%A, %d %B")}</div>',
            unsafe_allow_html=True
        )

    st.divider()



@st.dialog("ADD NEW WORKOUT", width="large")
def display_add_workout_plan_modal(userId):
    """
    Displays a modal for adding a new workout plan.
    """
    # --- 1. Basic Information ---
    
    # Added max_chars=50 here
    workout_name = st.text_input("WORKOUT NAME", max_chars=30, placeholder="e.g. Upper Body Blast, Leg Day...")

    col1, col2 = st.columns(2)
    with col1:
        workout_type = st.selectbox(
            "WORKOUT TYPE", 
            ["Strength", "Cardio", "HIIT", "Flexibility", "Yoga", "CrossFit", "Pilates", "Running", "Cycling", "Swimming", "Walking", "Other"], 
            index=None, placeholder="Select type"
        )
    with col2:
        muscle_groups = st.multiselect(
            "MUSCLE GROUPS", 
            ["Full Body", "Chest", "Back", "Shoulders", "Arms", "Core / Abs", "Legs", "Glutes", "Cardio (no target)"], 
            placeholder="Select targets"
        )

    # --- 2. Metrics ---
    col3, col4 = st.columns(2)
    with col3:
        duration = st.number_input("DURATION (MINUTES)", min_value=1, max_value=300, value=45, step=5)
    with col4:
        calories = st.number_input("TARGET CALORIES BURNED (OPTIONAL)", min_value=0, value=None, step=1, placeholder="e.g. 250")

    # --- 3. Date & Intensity ---
    workout_date = st.date_input("DATE", value=date.today())
    
    intensity = st.select_slider(
        "INTENSITY", 
        options=["Low", "Moderate", "High", "Max"], 
        value="Moderate"
    )

    st.divider()
    st.caption("EXERCISES")

    if "exercise_rows" not in st.session_state:
        st.session_state.exercise_rows = [{"name": "", "sets": 0, "reps": 0, "weight": "", "cardio_metric": ""}]

    def add_exercise():
        st.session_state.exercise_rows.append({"name": "", "sets": 0, "reps": 0, "weight": "", "cardio_metric": ""})

    def remove_exercise(index):
        if len(st.session_state.exercise_rows) > 1:
            st.session_state.exercise_rows.pop(index)

    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([2.0, 0.7, 0.7, 0.9, 1.1, 0.5])
    h_col1.markdown("**Exercise**")
    h_col2.markdown("**Sets**")
    h_col3.markdown("**Reps**")
    h_col4.markdown("**Weight**")
    h_col5.markdown("**Time / Dist**")

    # Loop through and generate inputs with max_chars added to text fields
    for i, row in enumerate(st.session_state.exercise_rows):
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([2.0, 0.7, 0.7, 0.9, 1.1, 0.5], vertical_alignment="center")
        
        with r_col1:
            row["name"] = st.text_input(f"Name {i}", value=row["name"], max_chars=50, key=f"name_{i}", label_visibility="collapsed", placeholder="e.g. Bench Press or Treadmill")
        with r_col2:
            row["sets"] = st.number_input(f"Sets {i}", value=row["sets"], min_value=0, key=f"sets_{i}", label_visibility="collapsed")
        with r_col3:
            row["reps"] = st.number_input(f"Reps {i}", value=row["reps"], min_value=0, key=f"reps_{i}", label_visibility="collapsed")
        with r_col4:
            row["weight"] = st.text_input(f"Weight / Level {i}", value=row["weight"], max_chars=20, key=f"weight_{i}", label_visibility="collapsed", placeholder="lbs/kg/mph")
        with r_col5:
            row["cardio_metric"] = st.text_input(f"Cardio {i}", value=row.get("cardio_metric", ""), max_chars=20, key=f"cardio_{i}", label_visibility="collapsed", placeholder="e.g. 30m, 5km")
        with r_col6:
            st.button("✕", key=f"del_{i}", on_click=remove_exercise, args=(i,))

    st.button("➕ Add exercise", on_click=add_exercise)

    st.divider()

    # --- 4. Notes & Action Buttons ---
    notes = st.text_area("NOTES", placeholder="Any extra details, rest times, technique cues...")

    spacer1, spacer2, btn_cancel, btn_save = st.columns([2, 1, 1, 1.5])
    
    with btn_cancel:
        if st.button("Cancel", use_container_width=True):
            if "exercise_rows" in st.session_state:
                del st.session_state.exercise_rows
            st.rerun()

    with btn_save:
        if st.button("Save Workout", type="primary", use_container_width=True):
            
            # --- VALIDATION BLOCK ---
            # We check the required fields. If any are missing, we show an error and STOP execution.
            if not workout_name.strip():
                st.error("Please enter a Workout Name.")
            elif not workout_type:
                st.error("Please select a Workout Type.")
            elif not muscle_groups or len(muscle_groups) == 0:
                st.error("Please select at least one Muscle Group.")
            elif not duration or duration <= 0:
                st.error("Please enter a valid Duration.")
            elif not workout_date:
                st.error("Please select a Date.")
            else:
                # If all checks pass, construct the data and save!
                workout_data = {
                    "name": workout_name.strip(),
                    "type": workout_type,
                    "muscle_groups": muscle_groups,
                    "duration": duration,
                    "calories": calories,
                    "date": workout_date,
                    "intensity": intensity,
                    "exercises": st.session_state.exercise_rows,
                    "notes": notes
                }
                
                # Save workout
                save_logged_workout(userId, workout_data)
                
                st.success("Workout Saved Successfully!")
                
                if "exercise_rows" in st.session_state:
                    del st.session_state.exercise_rows
                    
                st.rerun()

@st.dialog(" ", width="large")
def display_workout_details_modal(workout):
    """
    Displays a read-only modal showing the full details of a saved workout.
    Expects a 'workout' dictionary containing all joined database info.
    """
    
    # --- 1. TITLE ---
    st.markdown(f'<div class="custom-modal-title">{workout.get("workout_name", "Workout Details")}</div>', unsafe_allow_html=True)
    
    # --- 2. GENERAL INFO (Top Section) ---
    # Shifted left: Type, Duration, Intensity, Target Calories
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    met_col1.metric("Type", workout.get("workout_type", "-"))
    met_col2.metric("Duration", f"{workout.get('duration', 0)} min")
    met_col3.metric("Intensity", workout.get("intensity", "-"))
    
    # Handle calories cleanly if it's 0 or missing
    cals = workout.get("calories_burned")
    met_col4.metric("Target Calories", str(cals) if cals else "-")
    
    # Row 2: Muscle Groups (Centered, slightly bigger text)
    if workout.get("muscle_groups"):
        st.markdown(
            f"<div style='text-align: center; font-size: 1.15rem; margin-top: 25px; margin-bottom: 5px;'>"
            f"<strong>💪 Muscle Groups:</strong> {', '.join(workout['muscle_groups'])}"
            f"</div>", 
            unsafe_allow_html=True
        )

    # Row 3: Date (Smaller, grey, aligned left at the bottom of the metadata)
    st.markdown(
        f"<div style='text-align: left; color: #888888; font-size: 0.9rem; margin-top: 20px;'>"
        f"Date: {workout.get('workout_date', '')}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # --- 3. EXERCISES (Middle Section) ---
    st.markdown('<div class="section-label" style="margin-top: 0; padding-bottom: 10px;">Exercises</div>', unsafe_allow_html=True)
    
    if not workout.get("exercises"):
        st.info("No exercises were logged for this workout.")
    else:
        # Table Headers
        h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2.5, 1, 1, 1.5, 1.5])
        h_col1.markdown("**Name**")
        h_col2.markdown("**Sets**")
        h_col3.markdown("**Reps**")
        h_col4.markdown("**Weight**")
        h_col5.markdown("**Time / Dist**")
        
        # A subtle horizontal line to separate headers from data
        st.markdown("<hr style='margin: 5px 0 15px 0; border-top: 1px solid #444;'>", unsafe_allow_html=True)
        
        # Exercise Data Rows
        for ex in workout["exercises"]:
            r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2.5, 1, 1, 1.5, 1.5], vertical_alignment="center")
            r_col1.write(ex.get("name", ""))
            r_col2.write(str(ex.get("sets", "0")))
            r_col3.write(str(ex.get("reps", "0")))
            
            # Using 'or' so empty strings fallback to a clean dash
            r_col4.write(ex.get("weight") or "-")
            r_col5.write(ex.get("cardio_metric") or "-")

    # --- 4. NOTES (Bottom Section) ---
    if workout.get("notes") and workout["notes"].strip():
        st.divider()
        st.markdown('<div class="section-label" style="margin-top: 0; padding-bottom: 10px;">Notes</div>', unsafe_allow_html=True)
        # Using a container with elevated background creates a nice "reading box" feel
        with st.container(border=True):
            st.write(workout["notes"])

    st.divider()
    
    # Close button aligned to the right
    _, close_col = st.columns([4, 1])
    with close_col:
        if st.button("Close", type="primary", use_container_width=True):
            st.rerun()


def display_workout_plan_page(userId):
    """Displays the Workout Plan page with a card-based list and an add modal."""
    load_workout_plan_css()

    st.markdown('<div class="daily-goals-page">', unsafe_allow_html=True)

    display_workout_plan_header()

    st.markdown(
        '<div class="section-label">View your workout plans:</div>',
        unsafe_allow_html=True
    )

    workouts = get_logged_workouts(userId)

    if not workouts:
        st.write("No workout plans added yet.")
    else:
        for i, workout in enumerate(workouts):
            left_space, card_col, btn_col, right_space = st.columns([2.1, 6.0, 0.8, 1.1], vertical_alignment="center")

            with card_col:
                display_workout_plan_card(
                    workout["workout_name"],
                    workout["duration"],
                    workout["intensity"],
                    workout["workout_date"]
                )

            with btn_col:
                with st.container(key=f"play_container_{i}"):
                    if st.button("▶", key=f"play_btn_{i}"):
                        display_workout_details_modal(workout)
                        

    workout_plan_cta = st.container(key="workout_plan_cta")
    with workout_plan_cta:
        st.markdown('<div class="add-goal-label">Add new workout plan</div>', unsafe_allow_html=True)
        if st.button("✚", key="open_workout_plan_modal"):
            display_add_workout_plan_modal(userId)

    st.markdown('</div>', unsafe_allow_html=True)

    
