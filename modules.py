#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component


# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass

def display_activity_summary(workouts_list):
    """Displays an activity summary card using the 'activity_summary' HTML template.

    Renders a header with aggregate statistics (total workouts, total calories
    burned, total duration) and a scrollable list of individual workout rows,
    each showing the workout name, date, calories, and duration.

    workouts_list: a list of workout dicts, each containing:
        - 'name'     (str) : workout type, e.g. 'Running'
        - 'date'     (str) : date string,  e.g. 'Mar 15, 2024'
        - 'calories' (int) : calories burned during the workout
        - 'duration' (int) : duration of the workout in minutes

    Example:
        workouts = [
            {'name': 'Running', 'date': 'Mar 15, 2024', 'calories': 450, 'duration': 35},
            {'name': 'Cycling', 'date': 'Mar 14, 2024', 'calories': 380, 'duration': 45},
        ]
        display_activity_summary(workouts)
    """
    # Compute aggregate stats across all workouts
    total_workouts = len(workouts_list)
    total_calories = sum(w.get('calories', 0) for w in workouts_list)
    total_duration = sum(w.get('duration', 0) for w in workouts_list)

    data = {
        'TOTAL_WORKOUTS': total_workouts,
        'TOTAL_CALORIES': total_calories,
        'TOTAL_DURATION': total_duration,
    }

    html_file_name = "activity_summary"
    create_component(data, html_file_name)

def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
