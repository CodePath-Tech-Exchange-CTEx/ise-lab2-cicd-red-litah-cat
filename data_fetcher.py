#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import os
import random
import uuid
import os
import json
import requests
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
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
        ORDER BY StartTimestamp DESC
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

    # Gets all workouts
    workouts = get_user_workouts(user_id)

    # Return if no workouts found
    if not workouts:
        return {
            "advice_id": None,
            "timestamp": datetime.now().isoformat(),
            "content": "No workouts found yet. Let's get moving!",
            "image": None
        }

    latest_workout = workouts[0]

    vertexai.init(project=PROJECT_ID, location="us-central1")
    
    
    model = GenerativeModel("gemini-2.5-flash-lite",
                            system_instruction="You are a helpful and encouraging workout coach.")
    
    prompt = f"""
            The user just finished a workout with these stats:
            - Start Time: {latest_workout.get('start_timestamp')} 
            - End Time: {latest_workout.get('end_timestamp')}
            - Distance: {latest_workout.get('distance')} miles
            - Steps: {latest_workout.get('steps')} steps
            - Calories: {latest_workout.get('calories_burned')} calories
    
            Provide one to two sentence of expert, encouraging fitness advice based on these specific numbers.
            Also, provide 3 keywords for a matching stock photo (e.g., 'running shoes asphalt').
    """
    
    # Line Written By Gemini
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema={
            "type": "OBJECT",
            "properties": {
                "content": {"type": "STRING"},
                "image_keywords": {
                    "type": "STRING", 
                    "description": "3 to 5 single keywords separated ONLY by spaces. No commas, no phrases."
                }
            },
            "required": ["content", "image_keywords"]
        },
        ),
    )

    try:
        ai_response = json.loads(response.text)
    except json.JSONDecodeError:
        # Fallback if Gemini hallucinates non-JSON text
        ai_response = {"content": "Great job on your workout!", "image_keywords": "gym"}


    image_url = get_image_url_genai_advice(ai_response)

    unique_id = uuid.uuid4().hex[:8] # Line written by Gemini
    advice_id = f"ADV-{unique_id.upper()}" # Line written by Gemini

    return {"advice_id": advice_id,
            "timestamp": datetime.now(),
            "content": ai_response["content"],
            "image": image_url
            }

def get_image_url_genai_advice(ai_response):
    """
    Gets image for genai advice using unplash API.

    """
    UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

    # Line written by Gemini
    image_url = None
    if random.random() > 0: # 70% chance of an image
        search_terms = ai_response["image_keywords"].replace(" ", ",")

        unsplash_url = f"https://api.unsplash.com/photos/random?query={search_terms}&client_id={UNSPLASH_ACCESS_KEY}"

        try:
            response = requests.get(unsplash_url)
            # 2. Convert the response into a Python dictionary
            data = response.json()
            
            # 3. Index into the dictionary to find the 'regular' size image URL
            # The structure is: data -> 'urls' -> 'regular'
            image_url = data.get('urls', {}).get('regular')
            
        except Exception as e:
            print(f"Unsplash Error: {e}")
    
    return image_url



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