#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st


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
    """Displays a post with the author's username,
    profile image, timestamp, text content, and an optional post image."""
    data = {
        'USERNAME': username,
        'USER_IMAGE': user_image,
        'TIMESTAMP': timestamp,
        'CONTENT': content,
        'POST_IMAGE': post_image,
    }
    html_file_name = "posts"
    create_component(data, html_file_name, height= 500, scrolling=True)

def display_activity_summary(workouts_list):
    """Displays an activity summary card over a period of time.

    """
    # Compute aggregate stats across all workouts
    from datetime import datetime
    total_workouts = len(workouts_list)
    total_calories = sum(w.get('calories_burned', 0) for w in workouts_list)

    # Derive duration in minutes from start/end timestamps
    total_duration = 0
    for w in workouts_list:
        try:
            start = datetime.strptime(w['start_timestamp'], '%Y-%m-%d %H:%M:%S')
            end   = datetime.strptime(w['end_timestamp'],   '%Y-%m-%d %H:%M:%S')
            total_duration += int((end - start).total_seconds() / 60)
        except (KeyError, ValueError):
            pass

    # Weekly goal: cap at 7 days and compute bar fill percentage
    goal_days = min(total_workouts, 7)
    goal_pct  = round((goal_days / 7) * 100)

    data = {
        'TOTAL_WORKOUTS': total_workouts,
        'TOTAL_CALORIES': total_calories,
        'TOTAL_DURATION': total_duration,
        'GOAL_DAYS':      goal_days,
        'GOAL_PCT':       goal_pct,
    }

    html_file_name = "workout_summary"
    create_component(data, html_file_name)

def display_recent_workouts(workouts_list):
    """
    Displays a list of recent workouts using a custom HTML component.
    
    Input: a list of dictionaries containing workout stats from data_fetcher.py.
    Output: None.
    """
    if not workouts_list:
        st.info("No recent workouts found.")
        return

    for workout in workouts_list:
        # Mapping data_fetcher keys to HTML template placeholders.
        data = {
            'START_TIME': workout['start_timestamp'],
            'END_TIME': workout['end_timestamp'],
            'DISTANCE': f"{workout['distance']} km",
            'STEPS': workout['steps'],
            'CALORIES': workout['calories_burned'],
            'START_COORDS': f"{workout['start_lat_lng'][0]}, {workout['start_lat_lng'][1]}",
            'END_COORDS': f"{workout['end_lat_lng'][0]}, {workout['end_lat_lng'][1]}"
        }
        
        # This renders 'custom_components/workout_card.html'.
        html_file_name = "workout_card"
        create_component(data, "workout_card", 270, 500)

def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
