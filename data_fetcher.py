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

try:
    from google.auth.exceptions import DefaultCredentialsError
except ImportError:
    DefaultCredentialsError = Exception


def _get_bigquery_client():
    """Return a BigQuery client if credentials are available, otherwise None."""
    if not PROJECT_ID:
        return None
    try:
        return bigquery.Client(project=PROJECT_ID)
    except Exception as exc:
        if isinstance(exc, DefaultCredentialsError) or "DefaultCredentialsError" in type(exc).__name__:
            return None
        if "Could not automatically determine credentials" in str(exc):
            return None
        raise


def _safe_vertex_ai_init():
    if not PROJECT_ID:
        return False
    try:
        vertexai.init(project=PROJECT_ID, location="us-central1")
        return True
    except Exception:
        return False

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
    client = _get_bigquery_client()
    if client is None:
        return []

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

    client = _get_bigquery_client()
    if client is None:
        return [
            {
                "workout_id": "w1",
                "start_timestamp": "2026-04-18 09:00:00",
                "end_timestamp": "2026-04-18 09:30:00",
                "start_lat_lng": (37.7749, -122.4194),
                "end_lat_lng": (37.7758, -122.4188),
                "distance": 4.2,
                "steps": 5200,
                "calories_burned": 250,
            },
            {
                "workout_id": "w2",
                "start_timestamp": "2026-04-17 18:15:00",
                "end_timestamp": "2026-04-17 18:45:00",
                "start_lat_lng": (37.7749, -122.4194),
                "end_lat_lng": (37.7758, -122.4188),
                "distance": 3.0,
                "steps": 4300,
                "calories_burned": 210,
            },
        ]

    # Line written by Gemini.
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


def get_user_workout_plans(user_id):
    """Returns the user's saved structured workout plans."""
    # This is a sample implementation for saved workout plans.
    # In a full app, plans would come from a data store.
    return [
        {
            "plan_id": "plan_1",
            "name": "Full Body Strength",
            "duration": 35,
            "goal": "Build strength",
            "workout_count": 5,
            "exercises": [
                {"name": "Warm-up jog", "duration": "5 min"},
                {"name": "Squats", "sets_reps": "3x12", "rest": "60 sec"},
                {"name": "Push-ups", "sets_reps": "3x10", "rest": "45 sec"},
                {"name": "Dumbbell rows", "sets_reps": "3x12", "rest": "60 sec"},
                {"name": "Plank", "duration": "2 min", "notes": "Hold with core engaged."},
            ],
        },
        {
            "plan_id": "plan_2",
            "name": "Cardio & Core",
            "duration": 25,
            "goal": "Increase endurance",
            "workout_count": 4,
            "exercises": [
                {"name": "Jump rope", "duration": "5 min"},
                {"name": "High knees", "sets_reps": "3x45 sec", "rest": "30 sec"},
                {"name": "Mountain climbers", "sets_reps": "3x40 sec", "rest": "30 sec"},
                {"name": "Bicycle crunches", "sets_reps": "3x20", "rest": "30 sec"},
            ],
        },
        {
            "plan_id": "plan_3",
            "name": "Push Day Focus",
            "duration": 40,
            "goal": "Upper body strength",
            "workout_count": 5,
            "exercises": [
                {"name": "Dynamic warm-up", "duration": "5 min"},
                {"name": "Bench press", "sets_reps": "4x8", "rest": "90 sec"},
                {"name": "Overhead press", "sets_reps": "3x10", "rest": "75 sec"},
                {"name": "Tricep dips", "sets_reps": "3x12", "rest": "60 sec"},
                {"name": "Core stretch", "duration": "5 min"},
            ],
        },
    ]


def get_user_profile(user_id):
    """Returns information about the given user.

    """
    client = _get_bigquery_client()
    if client is None:
        return {
            'full_name': 'Remi',
            'username': 'remi_the_rems',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
            'friends': ['user2', 'user3', 'user4'],
        }

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
    client = _get_bigquery_client()
    if client is None:
        return [
            {
                "user_id": user_id,
                "post_id": "p1",
                "timestamp": "2026-04-18 08:00:00",
                "content": "Feeling strong after my workout today!",
                "image": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg",
            }
        ]

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
    client = _get_bigquery_client()
    if client is None:
        return [{"user_id": friend} for friend in users.get(user_id, {}).get('friends', [])]

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

    if not _safe_vertex_ai_init():
        return {
            "advice_id": "ADV-LOCAL",
            "timestamp": datetime.now(),
            "content": "Nice work! Keep up the momentum and hydrate after your workout.",
            "image": None,
        }

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
    client = _get_bigquery_client()
    if client is None:
        return
 
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

def get_chat_history(user_id):
    """Returns chat history for a given user from BigQuery."""
    client = _get_bigquery_client()
    if client is None:
        return []

    query = f"""
        SELECT MessageId, UserId, Timestamp, Role, Content
        FROM `{PROJECT_ID}.{COURSE_CODE}.ChatHistory`
        WHERE UserId = @user_id
        ORDER BY Timestamp ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    try:
        results = query_job.result()
    except Exception as e:
        # Table might not exist yet; return empty list gracefully
        print(f"Error fetching chat history: {e}")
        return []

    history = []
    for row in results:
        history.append({
            "message_id": row.MessageId,
            "user_id": row.UserId,
            "timestamp": row.Timestamp,
            "role": row.Role,
            "content": row.Content
        })

    return history

def insert_chat_message(user_id, role, content):
    """Inserts a new chat message into the BigQuery ChatHistory table."""
    client = _get_bigquery_client()
    if client is None:
        return

    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    query = f"""
        INSERT INTO `{PROJECT_ID}.{COURSE_CODE}.ChatHistory` (MessageId, UserId, Timestamp, Role, Content)
        VALUES (@message_id, @user_id, @timestamp, @role, @content)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("message_id", "STRING", message_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("timestamp", "STRING", timestamp),
            bigquery.ScalarQueryParameter("role", "STRING", role),
            bigquery.ScalarQueryParameter("content", "STRING", content),
        ]
    )

    query_job = client.query(query, job_config=job_config)
    query_job.result()

def get_fitness_profile(user_id):
    """Returns the saved fitness profile for a given user from BigQuery.
    Returns None if no profile has been saved yet.
    """
    client = _get_bigquery_client()
    if client is None:
        return None

    query = f"""
        SELECT
            FirstName, LastName, Age, Sex, Height, Weight,
            FitnessLevel, InjuriesLimitations, PrimaryGoal, UpdatedAt
        FROM `{PROJECT_ID}.{COURSE_CODE}.UserFitnessProfiles`
        WHERE UserId = @user_id
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        for row in results:
            return {
                "first_name": row.FirstName,
                "last_name": row.LastName,
                "age": row.Age,
                "sex": row.Sex,
                "height": row.Height,
                "weight": row.Weight,
                "fitness_level": row.FitnessLevel,
                "injuries_limitations": row.InjuriesLimitations,
                "primary_goal": row.PrimaryGoal,
                "updated_at": row.UpdatedAt,
            }
    except Exception as e:
        print(f"Error fetching fitness profile: {e}")

    return None


def save_fitness_profile(user_id, first_name, last_name, age, sex, height,
                         weight, fitness_level, injuries_limitations, primary_goal):
    """Saves (upserts) a user's fitness profile into BigQuery.

    Uses a MERGE statement so repeated saves update the existing row rather
    than inserting duplicates.
    """
    client = _get_bigquery_client()
    if client is None:
        return
    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # BigQuery MERGE (upsert) — insert if not exists, update if exists.
    query = f"""
        MERGE `{PROJECT_ID}.{COURSE_CODE}.UserFitnessProfiles` AS target
        USING (SELECT @user_id AS UserId) AS source
        ON target.UserId = source.UserId
        WHEN MATCHED THEN
            UPDATE SET
                FirstName = @first_name,
                LastName = @last_name,
                Age = @age,
                Sex = @sex,
                Height = @height,
                Weight = @weight,
                FitnessLevel = @fitness_level,
                InjuriesLimitations = @injuries_limitations,
                PrimaryGoal = @primary_goal,
                UpdatedAt = @updated_at
        WHEN NOT MATCHED THEN
            INSERT (UserId, FirstName, LastName, Age, Sex, Height, Weight,
                    FitnessLevel, InjuriesLimitations, PrimaryGoal, UpdatedAt)
            VALUES (@user_id, @first_name, @last_name, @age, @sex, @height,
                    @weight, @fitness_level, @injuries_limitations, @primary_goal, @updated_at)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("first_name", "STRING", first_name),
            bigquery.ScalarQueryParameter("last_name", "STRING", last_name),
            bigquery.ScalarQueryParameter("age", "INT64", int(age) if age else 0),
            bigquery.ScalarQueryParameter("sex", "STRING", sex),
            bigquery.ScalarQueryParameter("height", "STRING", height),
            bigquery.ScalarQueryParameter("weight", "STRING", weight),
            bigquery.ScalarQueryParameter("fitness_level", "STRING", fitness_level),
            bigquery.ScalarQueryParameter("injuries_limitations", "STRING", injuries_limitations),
            bigquery.ScalarQueryParameter("primary_goal", "STRING", primary_goal),
            bigquery.ScalarQueryParameter("updated_at", "STRING", updated_at),
        ]
    )

    query_job = client.query(query, job_config=job_config)
    query_job.result()


def chat_with_ai(user_id, user_message):
    """
    Sends a message to Vertex AI with full conversation context fetched from
    BigQuery on every call. Uses generate_content() with a reconstructed
    contents list so no stateful client object is needed between server restarts.
    """
    from vertexai.generative_models import Content, Part

    # Store the user's message first so it is included in history
    insert_chat_message(user_id, 'user', user_message)

    # Rebuild full conversation history from BigQuery on every call
    history = get_chat_history(user_id)

    # Reconstruct the contents list — Vertex AI only accepts 'user' or 'model'
    contents = []
    for msg in history:
        vertex_role = 'user' if msg['role'] == 'user' else 'model'
        contents.append(Content(role=vertex_role, parts=[Part.from_text(msg['content'])]))

    # Include fitness profile as context in the system instruction if available.
    profile = get_fitness_profile(user_id)
    if profile:
        profile_context = f"""
    User's Fitness Profile:
    - Name: {profile['first_name']} {profile['last_name']}
    - Age: {profile['age']}
    - Sex: {profile['sex']}
    - Height: {profile['height']}
    - Weight: {profile['weight']}
    - Fitness Level: {profile['fitness_level']}
    - Primary Goal: {profile['primary_goal']}
    - Injuries / Limitations: {profile['injuries_limitations'] or 'None'}

    Always personalise your advice using this profile.
"""
    else:
        profile_context = "\n    No fitness profile saved yet. Encourage the user to complete their profile.\n"

    vertexai.init(project=PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-2.5-flash-lite",
    system_instruction=f"""You are Arnold, an expert AI personal trainer and fitness coach. You have deep knowledge of strength training, cardio, nutrition, injury prevention, recovery, and workout programming.
{profile_context}
    You ONLY answer questions related to:
    - Exercise and workout programming
    - Fitness goals (weight loss, muscle building, flexibility, endurance)
    - Nutrition as it relates to fitness and performance
    - Recovery, sleep, and injury prevention
    - The user's personal training context provided above

    If a user asks about ANYTHING outside of fitness and training — coding, math, general knowledge, current events, or anything unrelated — you must politely decline and redirect. For example: "That's outside my expertise! I'm here strictly for your fitness journey. Ask me about your workouts, nutrition, or training plan instead."

    Tone: Direct, motivating, and knowledgeable. Like a real personal trainer who genuinely cares about results. Be concise — 2-4 sentences unless the user explicitly asks for detail or a full plan.

    Never break character. Never answer non-fitness questions even if the user insists."""
    )

    response = model.generate_content(contents=contents)
    ai_text = response.text

    # Persist the model's response using the correct role string
    insert_chat_message(user_id, 'model', ai_text)

    return ai_text