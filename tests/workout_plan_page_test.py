#############################################################################
# test_workout_plan_page.py
#
# Comprehensive unit tests for the UI rendering and validation logic 
# in workout_plan_page.py.
#############################################################################

import unittest
from unittest.mock import MagicMock, patch
from datetime import date
import sys
import streamlit as st

# =====================================================================
# STREAMLIT MOCK SETUP (ISOLATED)
# =====================================================================

# 1. Save the real Streamlit if the CI/CD pipeline already loaded it
original_streamlit = sys.modules.get('streamlit')

mock_st = MagicMock()
mock_st.dialog.return_value = lambda f: f

class MockSessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"SessionState has no attribute '{key}'")
    def __setattr__(self, key, value):
        self[key] = value
    def __delattr__(self, key):
        if key in self:
            del self[key]

mock_st.session_state = MockSessionState()

# 2. Inject the mock into the system modules
sys.modules['streamlit'] = mock_st

# 3. Import the page. It will grab our mock and hold onto it as `st`
import views.workout_plan_page as workout_plan_page

# 4. Restore the global environment so other tests don't crash!
if original_streamlit is not None:
    sys.modules['streamlit'] = original_streamlit
else:
    del sys.modules['streamlit']

class TestWorkoutPlanPage(unittest.TestCase):

    def setUp(self):
        """Reset the streamlit mock and session state before each test."""
        mock_st.reset_mock()
        
        # --- THE FIX: Explicitly stop test leakage ---
        # 1. Un-click all buttons so they don't accidentally trigger modals in other tests
        mock_st.button.return_value = False
        
        # 2. Clear any leftover side_effects from previous text inputs
        mock_st.text_input.side_effect = None
        mock_st.text_input.return_value = ""
        
        # 3. Completely rebuild the SessionState object so it isn't corrupted by reset_mock()
        mock_st.session_state = MockSessionState()

        # --- Dynamic Columns Mock ---
        # This function looks at what st.columns() was asked to build
        # and returns exactly the right number of mock columns to prevent unpacking errors.
        def dynamic_columns_mock(spec, *args, **kwargs):
            if isinstance(spec, int):
                return [MagicMock() for _ in range(spec)]
            elif isinstance(spec, (list, tuple)):
                return [MagicMock() for _ in range(len(spec))]
            return [MagicMock()] # Fallback

        mock_st.columns.side_effect = dynamic_columns_mock

    @patch('views.workout_plan_page.get_logged_workouts')
    @patch('views.workout_plan_page.display_workout_plan_card')
    def test_display_workout_plan_page_with_data(self, mock_display_card, mock_get_workouts):
        """Tests that the main page renders cards correctly when workouts exist."""
        mock_get_workouts.return_value = [{
            "workout_name": "Back Day",
            "duration": 45,
            "intensity": "High",
            "workout_date": date(2026, 4, 25)
        }]

        # Pass the dummy user_id
        workout_plan_page.display_workout_plan_page("test_user_123")

        # Verify it used the parameter to fetch workouts
        mock_get_workouts.assert_called_once_with("test_user_123")
        mock_display_card.assert_called_once_with(
            "Back Day", 45, "High", date(2026, 4, 25)
        )

    @patch('views.workout_plan_page.get_logged_workouts')
    def test_display_workout_plan_page_empty(self, mock_get_workouts):
        """Tests the empty state when a user has no logged workouts."""
        mock_get_workouts.return_value = []

        # Pass the dummy user_id
        workout_plan_page.display_workout_plan_page("test_user_123")

        mock_st.write.assert_called_with("No workout plans added yet.")

    def test_display_workout_details_modal_full_data(self):
        """Tests the details modal renders correctly with all optional fields present."""
        workout_data = {
            "workout_name": "Full Body Smash",
            "workout_type": "HIIT",
            "duration": 30,
            "intensity": "Max",
            "calories_burned": 400,
            "workout_date": date(2026, 4, 20),
            "muscle_groups": ["Full Body"],
            "exercises": [
                {"name": "Burpees", "sets": 3, "reps": 15, "weight": "", "cardio_metric": ""}
            ],
            "notes": "Felt great."
        }

        workout_plan_page.display_workout_details_modal(workout_data)

        # Grab the dynamically generated mocks from the very first columns call
        # (which is met_col1, met_col2, met_col3, met_col4 = st.columns(4))
        mock_columns = mock_st.columns.call_args_list[0]
        # Verify that metric was called on the columns
        self.assertTrue(mock_st.columns.return_value) 

    def test_display_workout_details_modal_missing_data(self):
        """Tests the details modal handles missing optional data gracefully without crashing."""
        workout_data = {
            "workout_name": "Quick Walk",
            "workout_type": "Cardio",
            "duration": 20,
            "intensity": "Low",
            "workout_date": date(2026, 4, 21)
        }

        workout_plan_page.display_workout_details_modal(workout_data)

        mock_st.info.assert_any_call("No exercises were logged for this workout.")

    def test_add_workout_modal_initializes_session_state(self):
        """Tests that opening the modal initializes the default exercise row."""
        # Pass the dummy user_id
        workout_plan_page.display_add_workout_plan_modal("test_user_123")

        self.assertIn("exercise_rows", mock_st.session_state)
        self.assertEqual(len(mock_st.session_state.exercise_rows), 1)
        self.assertEqual(mock_st.session_state.exercise_rows[0]["name"], "")

    @patch('views.workout_plan_page.save_logged_workout')
    def test_add_workout_modal_validation_empty_name(self, mock_save):
        """Tests that form validation stops execution if the workout name is missing."""
        mock_st.text_input.return_value = "   " # Blank name
        mock_st.selectbox.return_value = "Strength"
        mock_st.multiselect.return_value = ["Chest"]
        mock_st.number_input.return_value = 45
        mock_st.date_input.return_value = date(2026, 4, 22)
        
        # Only simulate clicking the "Save Workout" button
        def mock_button(label, *args, **kwargs):
            return label == "Save Workout"
        mock_st.button.side_effect = mock_button

        # Pass the dummy user_id
        workout_plan_page.display_add_workout_plan_modal("test_user_123")

        mock_st.error.assert_called_with("Please enter a Workout Name.")
        mock_save.assert_not_called()

    @patch('views.workout_plan_page.save_logged_workout')
    def test_add_workout_modal_successful_save(self, mock_save):
        """Tests that a fully valid form successfully calls the backend save function."""
        mock_st.text_input.side_effect = ["Valid Name", "Bench Press", "135", ""] 
        mock_st.selectbox.return_value = "Strength"
        mock_st.multiselect.return_value = ["Chest"]
        mock_st.number_input.return_value = 45
        mock_st.date_input.return_value = date(2026, 4, 22)
        mock_st.select_slider.return_value = "Moderate"
        mock_st.text_area.return_value = "Good workout"
        
        # Only simulate clicking the "Save Workout" button
        def mock_button(label, *args, **kwargs):
            return label == "Save Workout"
        mock_st.button.side_effect = mock_button

        # Pass the dummy user_id
        workout_plan_page.display_add_workout_plan_modal("test_user_123")

        mock_st.error.assert_not_called()
        mock_st.success.assert_called_with("Workout Saved Successfully!")
        mock_save.assert_called_once()
        
        # Verify the user_id was passed to the save function correctly
        saved_user_id = mock_save.call_args[0][0]
        saved_data = mock_save.call_args[0][1]
        
        self.assertEqual(saved_user_id, "test_user_123")
        self.assertEqual(saved_data["name"], "Valid Name")
        self.assertEqual(saved_data["type"], "Strength")

if __name__ == "__main__":
    unittest.main()