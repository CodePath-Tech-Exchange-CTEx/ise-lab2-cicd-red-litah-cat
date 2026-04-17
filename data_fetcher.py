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
from datetime import datetime, date
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

def _strip_markdown(text: str) -> str:
    """Removes common markdown formatting and escape sequences from a string,
    returning clean plain text suitable for display in HTML."""
    import re
    # Unescape backslash-escaped characters (e.g. \' -> ')
    text = text.replace("\\'", "'").replace('\\"', '"').replace("\\n", " ").replace("\\t", " ")
    # Remove bold/italic markers: **, *, __, _
    text = re.sub(r'\*{1,3}|_{1,3}', '', text)
    # Remove inline code backticks
    text = re.sub(r'`+', '', text)
    # Remove markdown headings (# Heading)
    text = re.sub(r'^\s*#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


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
    
    
    model = GenerativeModel(
        "gemini-2.5-flash-lite",
        system_instruction=(
            "You are a helpful and encouraging workout coach. "
            "Respond in plain text only. Do not use markdown formatting, "
            "asterisks, bold, italics, bullet points, or any escape characters."
        )
    )
    
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
            "content": _strip_markdown(ai_response["content"]),
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


def get_chat_history(user_id):
    """Returns chat history for a given user from BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)

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
        print(f"Error fetching chat history: {e}")
        return []

    history = []
    for row in results:
        history.append({
            "message_id": row.MessageId,
            "user_id": row.UserId,
            "timestamp": row.Timestamp,
            "role": row.Role,
            "content": _strip_markdown(row.Content or "")
        })

    return history


def insert_chat_message(user_id, role, content):
    """Inserts a new chat message into the BigQuery ChatHistory table."""
    client = bigquery.Client(project=PROJECT_ID)

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
    client = bigquery.Client(project=PROJECT_ID)

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
    client = bigquery.Client(project=PROJECT_ID)
    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

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
    """Sends a message to Vertex AI with full conversation context fetched from
    BigQuery on every call. Uses generate_content() with a reconstructed
    contents list so no stateful client object is needed between server restarts.

    Args:
        user_id (str): The ID of the current user.
        user_message (str): The message sent by the user.

    Returns:
        str: The AI model's reply text.
    """
    from vertexai.generative_models import Content, Part

    insert_chat_message(user_id, 'user', user_message)

    history = get_chat_history(user_id)

    contents = []
    for msg in history:
        vertex_role = 'user' if msg['role'] == 'user' else 'model'
        contents.append(Content(role=vertex_role, parts=[Part.from_text(msg['content'])]))

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
    model = GenerativeModel(
        "gemini-2.5-flash-lite",
        system_instruction=(
            f"You are Arnold, an expert AI personal trainer and fitness coach. "
            f"You have deep knowledge of strength training, cardio, nutrition, "
            f"injury prevention, recovery, and workout programming.\n"
            f"{profile_context}\n"
            "You ONLY answer questions related to:\n"
            "- Exercise and workout programming\n"
            "- Fitness goals (weight loss, muscle building, flexibility, endurance)\n"
            "- Nutrition as it relates to fitness and performance\n"
            "- Recovery, sleep, and injury prevention\n"
            "- The user's personal training context provided above\n\n"
            "If a user asks about ANYTHING outside of fitness and training — coding, math, "
            "general knowledge, current events, or anything unrelated — you must politely "
            "decline and redirect. For example: \"That's outside my expertise! I'm here "
            "strictly for your fitness journey. Ask me about your workouts, nutrition, or "
            "training plan instead.\"\n\n"
            "Tone: Direct, motivating, and knowledgeable. Like a real personal trainer who "
            "genuinely cares about results. Be concise — 2-4 sentences unless the user "
            "explicitly asks for detail or a full plan.\n\n"
            "Never break character. Never answer non-fitness questions even if the user insists.\n\n"
            "IMPORTANT: Respond in plain text only. Do not use markdown formatting of any kind — "
            "no asterisks, no bold, no italics, no bullet point dashes, no headers, no backticks, "
            "and no escape characters such as \\' or \\\"."
        )
    )

    response = model.generate_content(contents=contents)
    ai_text = _strip_markdown(response.text)

    insert_chat_message(user_id, 'model', ai_text)

    return ai_text

def get_daily_goals(user_id):
    """Displays daily workout goals."""
    client = bigquery.Client(project=PROJECT_ID)
    goal_date = date.today()

    query = f"""
        SELECT
            GoalId AS goal_id,
            UserId AS user_id,
            GoalName AS goal_name,
            Duration AS duration,
            Status AS status,
            GoalDate AS goal_date
        FROM `{PROJECT_ID}.{COURSE_CODE}.DailyGoals`
        WHERE UserId = @user_id AND GoalDate = @goal_date
        ORDER BY goal_name
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("goal_date", "DATE", goal_date),
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    daily_goals = []
    for row in results:
        daily_goals.append({
            "goal_id": row.goal_id,
            "user_id": row.user_id,
            "goal_name": row.goal_name,
            "duration": row.duration,
            "status": row.status,
            "goal_date": row.goal_date,
        })

    return daily_goals

def save_new_goal(user_id: str, goal_name: str, duration: int):
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        INSERT INTO `{PROJECT_ID}.{COURSE_CODE}.DailyGoals`
            (GoalId, UserId, GoalName, Duration, Status, GoalDate)
        VALUES (@goal_id, @user_id, @goal_name, @duration, FALSE, @goal_date)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("goal_id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("goal_name", "STRING", goal_name),
            bigquery.ScalarQueryParameter("duration", "INT64", duration),
            bigquery.ScalarQueryParameter("goal_date", "DATE", date.today()),
        ]
    )

    client.query(query, job_config=job_config).result()
    
def update_goal_status(goal_id: str, completed: bool):
    """Updates the completion status of a goal."""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        UPDATE `{PROJECT_ID}.{COURSE_CODE}.DailyGoals`
        SET Status = @completed
        WHERE GoalId = @goal_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("goal_id", "STRING", goal_id),
            bigquery.ScalarQueryParameter("completed", "BOOL", completed),
        ]
    )
    client.query(query, job_config=job_config).result()