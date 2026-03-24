#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import os
import random
import uuid
from datetime import datetime
from google.cloud import bigquery


# TODO: Rename ".env.template" to ".env" and add your project ID to it.
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")
COURSE_CODE = os.environ.get("COURSE_CODE")


users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}



def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestamped information for a given workout."""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT 
            st.Name AS SensorType,
            sd.Timestamp,
            sd.SensorValue AS Data,
            st.Units
        FROM `{PROJECT_ID}.{COURSE_CODE}.SensorData` sd
        JOIN `{PROJECT_ID}.{COURSE_CODE}.Workouts` w
            ON sd.WorkoutID = w.WorkoutId
        JOIN `{PROJECT_ID}.{COURSE_CODE}.SensorTypes` st
            ON sd.SensorId = st.SensorId
        WHERE w.UserId = @user_id AND sd.WorkoutID = @workout_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    sensor_data = []
    for row in results:
        sensor_data.append({
            "sensor_type": row.SensorType,
            "timestamp": row.Timestamp,
            "data": row.Data,
            "units": row.Units
        })

    return sensor_data

def get_user_workouts(user_id):
    """
    Fetches all workout records for a specific user from the BigQuery Workouts table.
    """

    # Line written by Gemini.
    client = bigquery.Client(project=PROJECT_ID)


    # The query retrieves workout metrics for the specific user from the Workouts table. Line written by Gemini.
    query = f"""
        SELECT 
            WorkoutId, 
            StartTimestamp, 
            EndTimestamp, 
            StartLocationLat, 
            StartLocationLong, 
            EndLocationLat, 
            EndLocationLong, 
            TotalDistance, 
            TotalSteps, 
            CaloriesBurned
        FROM `{PROJECT_ID}.{COURSE_CODE}.Workouts`
        WHERE UserId = @user_id
    """
    
    # We use parameterized queries to prevent SQL injection.
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    workouts = []
    for row in results:
        # We map the database columns to the dictionary keys required by the assignment. 
        workout_dict = {
            "workout_id": row.WorkoutId,
            "start_timestamp": row.StartTimestamp,
            "end_timestamp": row.EndTimestamp,
            "start_lat_lng": (row.StartLocationLat, row.StartLocationLong),
            "end_lat_lng": (row.EndLocationLat, row.EndLocationLong),
            "distance": row.TotalDistance,
            "steps": row.TotalSteps,
            "calories_burned": row.CaloriesBurned
        }
        workouts.append(workout_dict)

    return workouts


def get_user_profile(user_id):
    """Returns information about the given user.

    """
    client = bigquery.Client(project=PROJECT_ID)

    # Line written by Gemini
    query = f"""
        WITH all_friendships AS (
            SELECT UserId1 AS user_id, UserId2 AS friend_id FROM `{PROJECT_ID}.{COURSE_CODE}.Friends`
            UNION DISTINCT
            SELECT UserId2 AS user_id, UserId1 AS friend_id FROM `{PROJECT_ID}.{COURSE_CODE}.Friends`
        )

        SELECT
            u.Name AS full_name,
            u.Username AS username,
            u.DateOfBirth AS date_of_birth,
            u.ImageUrl AS profile_image,
            ARRAY_AGG(f.friend_id IGNORE NULLS) AS friends
        FROM
            `{PROJECT_ID}.{COURSE_CODE}.Users` AS u
        LEFT JOIN
            all_friendships AS f ON u.UserId = f.user_id
        WHERE u.UserId = @target_id
        GROUP BY
            u.UserId, u.Name, u.Username, u.DateOfBirth, u.ImageUrl
    """
    
    # Line written by Gemini
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("target_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    for row in results:
        return dict(row)

    raise ValueError(f'User {user_id} not found.')


def get_user_posts(user_id):
    """Returns a list of posts for the given user."""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            AuthorId AS user_id,
            PostId AS post_id,
            Timestamp AS timestamp,
            Content AS content,
            ImageUrl AS image
        FROM `{PROJECT_ID}.{COURSE_CODE}.Posts`
        WHERE AuthorId = @user_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    posts = []
    for row in results:
        post_dict = {
            "user_id": row.user_id,
            "post_id": row.post_id,
            "timestamp": row.timestamp,
            "content": row.content,
            "image": row.image
        }
        posts.append(post_dict)

    return posts

def get_user_friends(user_id):
    """Returns a user's friends"""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT UserId2 AS user_id
        FROM `{PROJECT_ID}.{COURSE_CODE}.Friends`
        WHERE UserId1 = @user_id

        UNION DISTINCT

        SELECT UserId1 AS user_id
        FROM `{PROJECT_ID}.{COURSE_CODE}.Friends`
        WHERE UserId2 = @user_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    friends = []
    for row in results:
        friend_dict = {
            "user_id": row.user_id
        }
        friends.append(friend_dict)

    return friends


def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.


    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }

def insert_post(user_id, content):
    """Inserts a new post into the BigQuery Posts table.
 
    Args:
        user_id: The ID of the user creating the post.
        content: The text content of the post.
    """
    client = bigquery.Client(project=PROJECT_ID)
 
    post_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
 
    query = f"""
        INSERT INTO `{PROJECT_ID}.{COURSE_CODE}.Posts` (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (@post_id, @user_id, @timestamp, NULL, @content)
    """
 
    # We use parameterized queries to prevent SQL injection.
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("post_id", "STRING", post_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("timestamp", "STRING", timestamp),
            bigquery.ScalarQueryParameter("content", "STRING", content),
        ]
    )
 
    query_job = client.query(query, job_config=job_config)
    query_job.result()