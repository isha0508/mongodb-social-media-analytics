"""
MongoDB-Based Social Media Analytics Dashboard

This dashboard visualizes analytics produced by MongoDB aggregation pipelines.
It uses the existing aggregation functions from analytics/aggregation_queries.py.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
import os

# Ensure analytics/ directory is importable
_project_root = os.path.dirname(os.path.abspath(__file__))
_analytics_dir = os.path.join(_project_root, "analytics")
if _analytics_dir not in sys.path:
    sys.path.insert(0, _analytics_dir)

# Import aggregation functions
from aggregation_queries import (
    get_overview_metrics,
    get_category_engagement,
    get_top_posts,
    get_top_users,
    get_activity_over_time,
    get_interaction_type_distribution,
    get_top_hashtags,
    get_sentiment_distribution,
    get_sentiment_by_category,
    get_location_engagement,
    get_peak_interaction_hours
)

# Configure the Streamlit page
st.set_page_config(
    page_title="MongoDB-Based Social Media Analytics",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Database Connection & Error Handling
# =============================================================================

def test_mongodb_connection():
    """Test MongoDB connection and return True if successful."""
    try:
        from database.connection import get_database
        db, client = get_database(server_timeout_ms=5000)
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False
    except Exception:
        return False

# Test connection at startup
if not test_mongodb_connection():
    st.error("""
    ### Unable to connect to MongoDB
    Please make sure the MongoDB service is running on localhost:27017.
    
    **To start MongoDB:**
    - Windows: Run `mongod` in command prompt
    - macOS/Linux: Run `sudo systemctl start mongod` or `mongod`
    """)
    st.stop()

# =============================================================================
# Cached Data Loading Functions
# =============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_overview_metrics():
    """Load overview KPI metrics."""
    return get_overview_metrics()

@st.cache_data(ttl=300)
def load_category_engagement(category=None):
    """Load category engagement data."""
    return get_category_engagement(category=category)

@st.cache_data(ttl=300)
def load_interaction_type_distribution():
    """Load interaction type distribution."""
    return get_interaction_type_distribution()

@st.cache_data(ttl=300)
def load_top_posts(limit, category=None):
    """Load top posts."""
    return get_top_posts(limit=limit, category=category)

@st.cache_data(ttl=300)
def load_top_users(limit):
    """Load top users."""
    return get_top_users(limit=limit)

@st.cache_data(ttl=300)
def load_top_hashtags(limit, category=None):
    """Load top hashtags."""
    return get_top_hashtags(limit=limit, category=category)

@st.cache_data(ttl=300)
def load_location_engagement():
    """Load location engagement data."""
    return get_location_engagement()

@st.cache_data(ttl=300)
def load_sentiment_distribution(sentiment=None, category=None):
    """Load sentiment distribution."""
    return get_sentiment_distribution(sentiment=sentiment, category=category)

@st.cache_data(ttl=300)
def load_sentiment_by_category(category=None, sentiment=None):
    """Load sentiment by category."""
    return get_sentiment_by_category(category=category, sentiment=sentiment)

@st.cache_data(ttl=300)
def load_activity_over_time(granularity):
    """Load activity over time."""
    return get_activity_over_time(granularity=granularity)

@st.cache_data(ttl=300)
def load_peak_interaction_hours():
    """Load peak interaction hours."""
    return get_peak_interaction_hours()

# =============================================================================
# Sidebar Configuration
# =============================================================================

with st.sidebar:
    st.title("Social Media Analytics", icon=":material/analytics:")
    st.caption("Interactive dashboard for MongoDB-based analytics")
    
    st.markdown("---")
    
    # Navigation
    page = st.selectbox(
        "Navigation",
        ["Overview", "Content & Engagement", "Users & Locations", "Sentiment Analysis", "Time & Activity"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Dataset Information
    st.subheader("Dataset Information", icon=":material/database:")
    metrics = load_overview_metrics()
    if metrics:
        st.metric("Users", f"{metrics.get('total_users', 0):,}")
        st.metric("Posts", f"{metrics.get('total_posts', 0):,}")
        st.metric("Comments", f"{metrics.get('total_comments', 0):,}")
        st.metric("Interactions", f"{metrics.get('total_interactions', 0):,}")
    else:
        st.warning("Unable to load dataset counts")
    
    st.markdown("---")
    
    # Global Filters
    st.subheader("Filters", icon=":material/filter_list:")
    
    # Category filter
    category_filter = st.selectbox(
        "Category",
        ["All", "Technology", "Sports", "Entertainment", "Travel", 
         "Education", "Food", "Fashion", "Business", "Health", "Environment"]
    )
    
    # Sentiment filter
    sentiment_filter = st.selectbox(
        "Sentiment",
        ["All", "Positive", "Neutral", "Negative"]
    )
    
    # Convert "All" to None for API calls
    category_param = None if category_filter == "All" else category_filter
    sentiment_param = None if sentiment_filter == "All" else sentiment_filter

# =============================================================================
# Main Page Header
# =============================================================================

st.title("MongoDB-Based Social Media Analytics", icon=":material/dashboard:")
st.caption("Interactive Social Media Data Analytics Dashboard")

# =============================================================================
# Active Filters Indicator
# =============================================================================

active_filters = []
if category_param is not None:
    active_filters.append(f"Category: {category_param}")
if sentiment_param is not None:
    active_filters.append(f"Sentiment: {sentiment_param}")

if active_filters:
    st.caption(f"Active filters: {', '.join(active_filters)}")
else:
    st.caption("Active filters: None")

# =============================================================================
# Page: Overview
# =============================================================================

if page == "Overview":
    st.header("Overview", icon=":material/analytics:")
    
    # Load metrics
    metrics = load_overview_metrics()
    
    if not metrics:
        st.warning("No data available for the selected filters.")
    else:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", f"{metrics.get('total_users', 0):,}")
        with col2:
            st.metric("Total Posts", f"{metrics.get('total_posts', 0):,}")
        with col3:
            st.metric("Total Comments", f"{metrics.get('total_comments', 0):,}")
        with col4:
            st.metric("Total Interactions", f"{metrics.get('total_interactions', 0):,}")
        
        st.space("small")
        
        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Total Views", f"{metrics.get('total_views', 0):,}")
        with col6:
            st.metric("Total Likes", f"{metrics.get('total_likes', 0):,}")
        with col7:
            st.metric("Total Shares", f"{metrics.get('total_shares', 0):,}")
        
        st.space("medium")
        
        # Chart 1: Engagement by Category
        st.subheader("Engagement by Category", icon=":material/bar_chart:")
        category_data = load_category_engagement(category=category_param)
        
        if category_data:
            df_category = pd.DataFrame(category_data)
            fig_category = px.bar(
                df_category,
                x='category',
                y='total_engagement',
                title='Total Engagement by Category',
                labels={'total_engagement': 'Total Engagement', 'category': 'Category'},
                color='total_engagement',
                color_continuous_scale='Blues'
            )
            fig_category.update_layout(xaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_category, width='stretch')
        else:
            st.warning("No category engagement data available.")
        
        st.space("medium")
        
        # Chart 2: Interaction Type Distribution
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Interaction Type Distribution", icon=":material/pie_chart:")
            interaction_data = load_interaction_type_distribution()
            
            if interaction_data:
                df_interaction = pd.DataFrame(interaction_data)
                fig_interaction = px.pie(
                    df_interaction,
                    values='count',
                    names='interaction_type',
                    title='Interaction Type Distribution',
                    hole=0.4
                )
                st.plotly_chart(fig_interaction, width='stretch')
            else:
                st.warning("No interaction type data available.")
        
        with col2:
            st.subheader("Top Posts", icon=":material/star:")
            top_posts = load_top_posts(limit=10, category=category_param)
            
            if top_posts:
                df_posts = pd.DataFrame(top_posts)
                display_cols = ['post_id', 'category', 'views', 'likes', 'shares', 'comment_count', 'total_engagement']
                df_display = df_posts[display_cols]
                st.dataframe(df_display, width='stretch', hide_index=True)
            else:
                st.warning("No top posts data available.")

# =============================================================================
# Page: Content & Engagement
# =============================================================================

elif page == "Content & Engagement":
    st.header("Content & Engagement", icon=":material/article:")
    
    # Section 1: Category Engagement
    st.subheader("Category Engagement", icon=":material/bar_chart:")
    category_data = load_category_engagement(category=category_param)
    
    if category_data:
        df_category = pd.DataFrame(category_data)
        
        # Metric selector
        metric = st.selectbox(
            "Select Metric",
            ["Total Engagement", "Views", "Likes", "Shares", "Number of Posts"]
        )
        
        metric_map = {
            "Total Engagement": "total_engagement",
            "Views": "total_views",
            "Likes": "total_likes",
            "Shares": "total_shares",
            "Number of Posts": "post_count"
        }
        
        y_column = metric_map[metric]
        
        fig_category = px.bar(
            df_category,
            x='category',
            y=y_column,
            title=f'{metric} by Category',
            labels={y_column: metric, 'category': 'Category'},
            color=y_column,
            color_continuous_scale='Viridis'
        )
        fig_category.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_category, width='stretch')
    else:
        st.warning("No category engagement data available.")
    
    st.space("medium")
    
    # Section 2: Top Hashtags
    st.subheader("Top Hashtags", icon=":material/tag:")
    hashtag_data = load_top_hashtags(limit=10, category=category_param)
    
    if hashtag_data:
        df_hashtags = pd.DataFrame(hashtag_data)
        fig_hashtags = px.bar(
            df_hashtags,
            x='usage_count',
            y='hashtag',
            orientation='h',
            title='Top 10 Hashtags by Usage Count',
            labels={'usage_count': 'Usage Count', 'hashtag': 'Hashtag'},
            color='usage_count',
            color_continuous_scale='Plasma'
        )
        fig_hashtags.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_hashtags, width='stretch')
    else:
        st.warning("No hashtag data available.")
    
    st.space("medium")
    
    # Section 3: Most Popular Posts
    st.subheader("Most Popular Posts", icon=":material/star:")
    limit = st.slider("Number of Posts", min_value=5, max_value=20, value=10, step=5)
    
    top_posts = load_top_posts(limit=limit, category=category_param)
    
    if top_posts:
        df_posts = pd.DataFrame(top_posts)
        display_cols = ['post_id', 'category', 'views', 'likes', 'shares', 'comment_count', 'total_engagement']
        df_display = df_posts[display_cols]
        st.dataframe(df_display, width='stretch', hide_index=True)
    else:
        st.warning("No top posts data available.")

# =============================================================================
# Page: Users & Locations
# =============================================================================

elif page == "Users & Locations":
    st.header("Users & Locations", icon=":material/people:")
    
    # Section 1: Most Active Users
    st.subheader("Most Active Users", icon=":material/person:")
    top_users = load_top_users(limit=10)
    
    if top_users:
        df_users = pd.DataFrame(top_users)
        display_cols = ['username', 'location', 'followers', 'total_interactions', 
                      'total_likes', 'total_comments', 'total_shares', 'total_views']
        df_display = df_users[display_cols]
        st.dataframe(df_display, width='stretch', hide_index=True)
    else:
        st.warning("No top users data available.")
    
    st.space("medium")
    
    # Section 2: Location Analytics
    st.subheader("Location Analytics", icon=":material/location_on:")
    location_data = load_location_engagement()
    
    if location_data:
        df_location = pd.DataFrame(location_data)
        fig_location = px.bar(
            df_location,
            x='location',
            y='total_interactions',
            title='Total Interactions by Location',
            labels={'total_interactions': 'Total Interactions', 'location': 'Location'},
            color='total_interactions',
            color_continuous_scale='Teal'
        )
        fig_location.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_location, width='stretch')
    else:
        st.warning("No location data available.")
    
    st.space("medium")
    
    # Section 3: User Activity Comparison
    st.subheader("User Activity Comparison", icon=":material/compare_arrows:")
    
    if top_users:
        df_users = pd.DataFrame(top_users)
        fig_scatter = px.scatter(
            df_users,
            x='followers',
            y='total_interactions',
            title='Followers vs Total Interactions (Top Users)',
            labels={'followers': 'Followers', 'total_interactions': 'Total Interactions'},
            hover_data=['username', 'location'],
            color='total_interactions',
            color_continuous_scale='Inferno'
        )
        st.plotly_chart(fig_scatter, width='stretch')
    else:
        st.warning("No user data available for comparison.")

# =============================================================================
# Page: Sentiment Analysis
# =============================================================================

elif page == "Sentiment Analysis":
    st.header("Sentiment Analysis", icon=":material/sentiment_satisfied:")
    
    # Section 1: Sentiment Distribution
    st.subheader("Sentiment Distribution", icon=":material/pie_chart:")
    sentiment_data = load_sentiment_distribution(sentiment=sentiment_param, category=category_param)
    
    if sentiment_data:
        df_sentiment = pd.DataFrame(sentiment_data)
        fig_sentiment = px.pie(
            df_sentiment,
            values='comment_count',
            names='sentiment',
            title='Sentiment Distribution of Comments',
            hole=0.4,
            color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
        )
        st.plotly_chart(fig_sentiment, width='stretch')
    else:
        st.warning("No sentiment distribution data available.")
    
    st.space("medium")
    
    # Section 2: Sentiment by Category
    st.subheader("Sentiment by Category", icon=":material/bar_chart:")
    sentiment_category_data = load_sentiment_by_category(category=category_param, sentiment=sentiment_param)
    
    if sentiment_category_data:
        df_sentiment_cat = pd.DataFrame(sentiment_category_data)
        fig_sentiment_cat = px.bar(
            df_sentiment_cat,
            x='category',
            y='comment_count',
            color='sentiment',
            title='Sentiment Breakdown by Category',
            labels={'comment_count': 'Number of Comments', 'category': 'Category'},
            color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
        )
        st.plotly_chart(fig_sentiment_cat, width='stretch')
    else:
        st.warning("No sentiment by category data available.")
    
    st.space("medium")
    
    # Section 3: Sentiment Summary Table
    st.subheader("Sentiment Summary", icon=":material/table_chart:")
    
    if sentiment_data:
        df_sentiment = pd.DataFrame(sentiment_data)
        df_sentiment = df_sentiment.rename(columns={'comment_count': 'Comments'})
        st.dataframe(df_sentiment, width='stretch', hide_index=True)
    else:
        st.warning("No sentiment summary data available.")

# =============================================================================
# Page: Time & Activity
# =============================================================================

elif page == "Time & Activity":
    st.header("Time & Activity", icon=":material/schedule:")
    
    # Section 1: Activity Over Time
    st.subheader("Activity Over Time", icon=":material/show_chart:")
    granularity_display = st.selectbox("Granularity", ["Daily", "Monthly"])
    granularity = "day" if granularity_display == "Daily" else "month"
    
    activity_data = load_activity_over_time(granularity=granularity)
    
    if activity_data:
        df_activity = pd.DataFrame(activity_data)
        fig_activity = px.line(
            df_activity,
            x='period',
            y='interaction_count',
            title=f'Interaction Count Over Time ({granularity_display})',
            labels={'interaction_count': 'Interaction Count', 'period': 'Date'}
        )
        st.plotly_chart(fig_activity, width='stretch')
    else:
        st.warning("No activity over time data available.")
    
    st.space("medium")
    
    # Section 2: Peak Interaction Hours
    st.subheader("Peak Interaction Hours", icon=":material/access_time:")
    peak_hours = load_peak_interaction_hours()
    
    if peak_hours:
        df_hours = pd.DataFrame(peak_hours)
        # Ensure all hours 0-23 are present
        all_hours = pd.DataFrame({'hour': range(24)})
        df_hours = all_hours.merge(df_hours, on='hour', how='left').fillna(0)
        
        fig_hours = px.bar(
            df_hours,
            x='hour',
            y='interaction_count',
            title='Interactions by Hour of Day',
            labels={'interaction_count': 'Interactions', 'hour': 'Hour of Day'},
            color='interaction_count',
            color_continuous_scale='Spectral'
        )
        fig_hours.update_layout(xaxis={'tickmode': 'linear', 'tick0': 0, 'dtick': 2})
        st.plotly_chart(fig_hours, width='stretch')
    else:
        st.warning("No peak hours data available.")

# =============================================================================
# Explainability Section
# =============================================================================

st.space("large")
st.header("How the Analytics Work", icon=":material/help:")

with st.expander("About MongoDB Aggregation Pipelines", icon=":material/code:"):
    st.markdown("""
    The dashboard retrieves data from MongoDB and uses aggregation pipelines
    to group, filter, sort, join, and summarize social-media data.
    
    **Key MongoDB operations used:**
    
    - **`$match`**: Filters documents to pass only those that match the specified condition
    - **`$group`**: Groups documents together by a specified field and performs aggregations
    - **`$sort`**: Sorts documents in ascending or descending order
    - **`$project`**: Reshapes documents by including, excluding, or renaming fields
    - **`$lookup`**: Performs a left outer join to another collection
    - **`$unwind`**: Deconstructs an array field into individual documents
    - **`$limit`**: Limits the number of documents passed to the next stage
    - **`$dateToString`**: Converts a date object to a string based on a format
    - **`$hour`**: Extracts the hour component from a date
    
    **Engagement Calculation:**
    
    ```
    Engagement = Likes + Shares + Comments
    ```
    
    This metric is computed directly in MongoDB using the `$add` operator in aggregation pipelines.
    """)

# =============================================================================
# Dataset Information Section
# =============================================================================

with st.expander("About the Dataset", icon=":material/database:"):
    st.markdown("""
    **Dataset Characteristics:**
    
    - This is a **synthetic dataset** generated specifically for this academic project
    - It simulates realistic social media user engagement and content trends
    
    **Dataset Size:**
    
    - **Users**: 1,000 user profiles with demographics and follower counts
    - **Posts**: 5,000 social media posts across 10 categories
    - **Comments**: 15,000 post comments with sentiment labels
    - **Interactions**: 20,000 engagement events (views, likes, shares, comments)
    
    **Available Categories:**
    
    Technology, Sports, Entertainment, Travel, Education, Food, Fashion, Business, Health, Environment
    
    **Sentiment Labels:**
    
    - Positive
    - Neutral
    - Negative
    
    **Interaction Types:**
    
    - View
    - Like
    - Share
    - Comment
    
    **Date/Time Information:**
    
    - Timestamps span a 12-month period
    - Interaction hours cover all 24 hours of the day
    - All dates are stored as native BSON Date objects in MongoDB
    """)
