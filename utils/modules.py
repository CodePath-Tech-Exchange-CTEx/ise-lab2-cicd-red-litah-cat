#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from utils.internals import create_component, load_html_file, safe_string
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import html as _html


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
    # of the HTML file. HTML must be placed inside the "components" folder.
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
    create_component(data, html_file_name, height= 300, scrolling=True)

def display_activity_summary(workouts_list):
    """
    Displays an activity summary card over a period of time based on a list of workouts.
    
    Input: A list of workout dictionaries containing start/end timestamps and calories.
    Output: None.
    """
    
    # Compute aggregate stats across all workouts.
    total_workouts = len(workouts_list)
    total_calories = sum(w.get('calories_burned') or 0 for w in workouts_list)

    # Derive duration in minutes from start/end timestamps.
    total_duration = 0
    for w in workouts_list:
        start = w.get('start_timestamp')
        end = w.get('end_timestamp')
        
        # Only calculate if both timestamps exist to avoid logic errors.
        if start and end:
            try:
                # Handle cases where DB returns strings vs. datetime objects.
                if isinstance(start, str):
                    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                    end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                else:
                    start_dt, end_dt = start, end
                
                duration_seconds = (end_dt - start_dt).total_seconds()
                total_duration += int(max(0, duration_seconds) / 60)
            except (ValueError, TypeError):
                # If timestamp format is invalid, we skip this specific workout.
                pass

    # Weekly goal: cap at 7 days and compute bar fill percentage.
    goal_days = min(total_workouts, 7)
    goal_pct = round((goal_days / 7) * 100) if total_workouts > 0 else 0

    data = {
        'TOTAL_WORKOUTS': total_workouts,
        'TOTAL_CALORIES': int(total_calories),
        'TOTAL_DURATION': total_duration,
        'GOAL_DAYS':      goal_days,
        'GOAL_PCT':       goal_pct,
    }

    html_file_name = "activity_summary"
    create_component(data, html_file_name, height=520, scrolling=False)

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
        
        create_component(data, "workout_summary_card", 270, 500)

def display_genai_advice(timestamp, content, image):
    """Write a good docstring here.
    
    Displays advice given from genai

    Args
        timestamp (str): The time the advice was generated.
        content (str): The generated advice text.
        image (str): Path to a motivational image.
    Returns
        None

    """
    data = {'TIMESTAMP': timestamp,
            'CONTENT': content,
            'IMAGE': image}

    html_file_name = 'display_genai_advice_component'
    create_component(data, html_file_name, height=500, scrolling=True)


def display_ai_trainer_hero(user_name):
    """Displays the hero greeting for the AI Trainer page.

    Renders a centred greeting ("Hello, <name>!!").

    Args:
        user_name (str): The user's display name to show in the greeting.
    """
    data = {'USER_NAME': user_name}
    create_component(data, "ai_trainer_hero", height=120)


def display_chat_history(messages):
    """Renders the full chat history as a single HTML component.

    Assembles all message bubbles in Python using the user and AI fragment
    templates, then injects the result into the wrapper which contains all
    necessary CSS. A single iframe is rendered for the whole thread.

    Args:
        messages (list): List of dicts with keys 'role', 'content', 'timestamp'.
                         Role must be 'user' or 'model'.
    """
    user_tmpl = load_html_file('components/chat_message_user.html')
    ai_tmpl = load_html_file('components/chat_message_ai.html')

    assembled_html = ""
    for msg in messages:
        timestamp_str = (
            msg['timestamp'].strftime('%Y-%m-%d %H:%M')
            if hasattr(msg['timestamp'], 'strftime')
            else str(msg['timestamp'])
        )
        content_safe = _html.escape(str(msg['content']))
        timestamp_safe = _html.escape(timestamp_str)

        if msg['role'] == 'user':
            bubble = (user_tmpl
                      .replace('{{CONTENT}}', content_safe)
                      .replace('{{TIMESTAMP}}', timestamp_safe))
        else:
            bubble = (ai_tmpl
                      .replace('{{CONTENT}}', content_safe)
                      .replace('{{TIMESTAMP}}', timestamp_safe))

        assembled_html += bubble + "\n"

    wrapper = load_html_file('components/chat_feed_wrapper.html')
    wrapper = wrapper.replace('{{INNER_HTML}}', assembled_html)

    height = max(300, min(len(messages) * 110, 500))
    components.html(wrapper, height=height, scrolling=True)

def display_goals(goal_name, duration, status):
    duration = f"{duration} min"
    check_mark = "✓" if status else ""

    data = {
        "GOAL_NAME": goal_name,
        "DURATION": duration,
        "CHECK_MARK": check_mark
    }

    create_component(data, "daily_goals", height=120, scrolling=False)


def display_workout_plan_card(workout_name, duration, intensity, workout_date):
    """Displays a single logged workout as a white rounded card.

    Args:
        workout_name (str): The name of the workout (e.g. 'Running').
        duration (int): Duration of the workout in minutes.
        intensity (str): Intensity level (e.g. 'Moderate').
        workout_date: The date the workout was performed.
    """
    data = {
        "WORKOUT_NAME": workout_name,
        "DURATION": str(duration),
        "INTENSITY": intensity,
        "WORKOUT_DATE": str(workout_date),
    }
    create_component(data, "workout_plan_card", height=120, scrolling=False)