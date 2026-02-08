import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Alden's Data Science Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Functions to fetch GitHub data
@st.cache_data
def fetch_github_user_data(username):
    """Fetch GitHub user profile data"""
    try:
        url = f'https://api.github.com/users/{username}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"User '{username}' not found")
            return None
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return None

@st.cache_data
def fetch_github_repos(username):
    """Fetch GitHub repositories"""
    try:
        url = f'https://api.github.com/users/{username}/repos?sort=updated&per_page=100'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching repos: {e}")
        return []

@st.cache_data
def fetch_github_languages(username):
    """Fetch language statistics from repositories"""
    try:
        repos = fetch_github_repos(username)
        languages = {}
        
        for repo in repos:
            if repo['language']:
                languages[repo['language']] = languages.get(repo['language'], 0) + 1
        
        return languages
    except Exception as e:
        st.error(f"Error fetching languages: {e}")
        return {}

# Sidebar
with st.sidebar:
    st.title("⚙️ Dashboard Settings")
    github_username = st.text_input("GitHub Username:", value="aldennabil")
    refresh_button = st.button("🔄 Refresh Data")

# Main content
if github_username:
    user_data = fetch_github_user_data(github_username)
    
    if user_data:
        # Header section
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"<h1 class='main-title'>👋 Welcome to {user_data.get('name', github_username)}'s Dashboard</h1>", unsafe_allow_html=True)
        
        with col2:
            if user_data.get('avatar_url'):
                st.image(user_data['avatar_url'], width=100)
        
        # Bio section
        if user_data.get('bio'):
            st.info(f"📝 {user_data['bio']}")
        
        # Statistics section
        st.markdown("---")
        st.subheader("📈 GitHub Statistics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Public Repos", user_data.get('public_repos', 0))
        
        with col2:
            st.metric("Followers", user_data.get('followers', 0))
        
        with col3:
            st.metric("Following", user_data.get('following', 0))
        
        with col4:
            st.metric("Public Gists", user_data.get('public_gists', 0))
        
        with col5:
            member_since = user_data.get('created_at', '').split('T')[0]
            st.metric("Member Since", member_since)
        
        # Profile information
        st.markdown("---")
        st.subheader("👤 Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Location:** {user_data.get('location', 'Not specified')}")
            st.write(f"**Company:** {user_data.get('company', 'Not specified')}")
            st.write(f"**Email:** {user_data.get('email', 'Not specified')}")
        
        with col2:
            st.write(f"**Blog:** {user_data.get('blog', 'Not specified')}")
            st.write(f"**Twitter:** {user_data.get('twitter_username', 'Not specified')}")
            if user_data.get('hireable'):
                st.write("✅ **Available for hire**")
        
        # Projects section
        st.markdown("---")
        st.subheader("📁 Top Projects")
        
        repos = fetch_github_repos(github_username)
        
        if repos:
            # Sort by stars and get top 6
            sorted_repos = sorted(repos, key=lambda x: x['stargazers_count'], reverse=True)[:6]
            
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            
            for idx, repo in enumerate(sorted_repos):
                with cols[idx % 3]:
                    with st.container():
                        st.write(f"### [{repo['name']}]({repo['html_url']})")
                        st.write(f"*{repo['description'] if repo['description'] else 'No description'}*")
                        
                        repo_col1, repo_col2, repo_col3 = st.columns(3)
                        with repo_col1:
                            st.write(f"⭐ {repo['stargazers_count']}")
                        with repo_col2:
                            st.write(f"🔀 {repo['forks_count']}")
                        with repo_col3:
                            if repo['language']:
                                st.write(f"🔤 {repo['language']}")
        
        # Programming Languages
        st.markdown("---")
        st.subheader("💻 Programming Languages")
        
        languages = fetch_github_languages(github_username)
        
        if languages:
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a bar chart
                fig = go.Figure(data=[
                    go.Bar(x=list(languages.keys()), y=list(languages.values()), marker_color='#1f77b4')
                ])
                fig.update_layout(
                    title="Language Distribution",
                    xaxis_title="Language",
                    yaxis_title="Number of Repositories",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create a pie chart
                fig = go.Figure(data=[
                    go.Pie(labels=list(languages.keys()), values=list(languages.values()))
                ])
                fig.update_layout(
                    title="Language Breakdown",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.markdown(f"<p style='text-align: center; color: grey;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

else:
    st.warning("Please enter a GitHub username to view the dashboard")
