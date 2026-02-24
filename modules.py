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
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """
    Displays a list of recent workouts using a custom HTML component.
    
    Input: a list of dictionaries containing workout stats from data_fetcher.py.
    Output: None.
    """
pass

def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
