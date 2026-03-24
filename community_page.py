import streamlit as st
from modules import display_post, display_genai_advice
from data_fetcher import get_user_posts, get_user_friends, get_genai_advice

userId = 'user2'

def display_community_page():
    """displays the community page including:
    First 10 posts from a user’s friends ordered by timestamp
    One piece of GenAI advice and encouragement
"""
    st.header("Community")

    st.divider()
    st.header("POSTS")

    #POSTS
    user_friends = get_user_friends(userId)
    posts = []
    for friend in user_friends:
        posts.extend(get_user_posts(friend['user_id']))
    posts.sort(key=lambda x: x['timestamp'], reverse=True)
    posts = posts[:10]

    #GENAI
    genai_advice = get_genai_advice(userId)

    #DISPLAY
    #st.divider()
    #st.subheader("POSTS")
    for post in posts:
        display_post(post['user_id'], None, post['timestamp'], post['content'], post['image'])

    st.divider()
    st.subheader("GENAI ADVICE")
    display_genai_advice(genai_advice['timestamp'], genai_advice['content'], genai_advice['image'])

if __name__ == '__main__':
    display_community_page()




