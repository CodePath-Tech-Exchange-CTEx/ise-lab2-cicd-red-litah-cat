#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import random
import uuid
from datetime import datetime
from google.cloud import bigquery

PROJECT_ID = "shamshad-ansari-fisk"
COURSE_CODE = "ISE"


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
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    sensor_data = []
    sensor_types = [
        'accelerometer',
        'gyroscope',
        'pressure',
        'temperature',
        'heart_rate',
    ]
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59))
        if len(random_minute) == 1:
            random_minute = '0' + random_minute
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        data = random.random() * 100
        sensor_type = random.choice(sensor_types)
        sensor_data.append(
            {'sensor_type': sensor_type, 'timestamp': timestamp, 'data': data}
        )
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

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


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

    This function currently returns random data. You will re-write it in Unit 3.
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