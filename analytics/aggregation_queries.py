"""
MongoDB Aggregation Queries Module
Phase 4: MongoDB Aggregation Pipelines & Analytics

All analytical calculations are performed inside MongoDB using aggregation
pipelines. Each function returns a list of plain Python dictionaries.
"""

import os
import sys

# Ensure database/ directory is importable for connection module
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_database_dir = os.path.join(_project_root, "database")
if _database_dir not in sys.path:
    sys.path.insert(0, _database_dir)

from connection import get_database


def _get_db():
    """Internal helper: returns an open (db, client) pair."""
    return get_database()


# ===========================================================================
# 1. KPI / Overview Analytics
# ===========================================================================

def get_overview_metrics():
    """
    Returns high-level KPI counts across all four collections.

    Counts: total users, total posts, total comments, total interactions,
    total views, total likes, total shares.

    All counts and sums are computed directly in MongoDB.

    Returns:
        dict: keys are metric names, values are integer counts/sums.
    """
    db, client = _get_db()
    try:
        total_users = db.users.count_documents({})
        total_posts = db.posts.count_documents({})
        total_comments = db.comments.count_documents({})
        total_interactions = db.interactions.count_documents({})

        # Aggregate totals for numeric engagement fields from posts
        agg = list(db.posts.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_views": {"$sum": "$views"},
                    "total_likes": {"$sum": "$likes"},
                    "total_shares": {"$sum": "$shares"}
                }
            }
        ]))

        if agg:
            return {
                "total_users": total_users,
                "total_posts": total_posts,
                "total_comments": total_comments,
                "total_interactions": total_interactions,
                "total_views": agg[0]["total_views"],
                "total_likes": agg[0]["total_likes"],
                "total_shares": agg[0]["total_shares"]
            }
        return {
            "total_users": total_users,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_interactions": total_interactions,
            "total_views": 0,
            "total_likes": 0,
            "total_shares": 0
        }
    except Exception:
        return {}
    finally:
        client.close()


# ===========================================================================
# 2. Engagement by Category
# ===========================================================================

def get_category_engagement(category=None):
    """
    For each post category, calculates the number of posts, total views,
    total likes, total shares, and total engagement.

    engagement = likes + shares + comment_count

    Uses:
        posts collection -> $group by category (views/likes/shares)
        comments collection -> $group by post_id to count comments
        $lookup to join comment counts back to posts
        $unwind, $group, $project, $sort

    Args:
        category (str, optional): Filter to a specific category. If None, returns all categories.

    Returns:
        list[dict]: one record per category, sorted by total_engagement desc.
    """
    db, client = _get_db()
    try:
        pipeline = []
        
        # Add category filter if specified
        if category is not None:
            pipeline.append({"$match": {"category": category}})
        
        # Step 1: Join comments into each post document
        pipeline.append({
            "$lookup": {
                "from": "comments",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "post_comments"
            }
        })
        # Step 2: Project per-post comment count + engagement fields
        pipeline.append({
            "$project": {
                "_id": 0,
                "category": 1,
                "views": 1,
                "likes": 1,
                "shares": 1,
                "comment_count": {"$size": "$post_comments"}
            }
        })
        # Step 3: Group by category
        pipeline.append({
            "$group": {
                "_id": "$category",
                "post_count": {"$sum": 1},
                "total_views": {"$sum": "$views"},
                "total_likes": {"$sum": "$likes"},
                "total_shares": {"$sum": "$shares"},
                "total_comments": {"$sum": "$comment_count"}
            }
        })
        # Step 4: Compute total engagement
        pipeline.append({
            "$project": {
                "_id": 0,
                "category": "$_id",
                "post_count": 1,
                "total_views": 1,
                "total_likes": 1,
                "total_shares": 1,
                "total_comments": 1,
                "total_engagement": {
                    "$add": ["$total_likes", "$total_shares", "$total_comments"]
                }
            }
        })
        pipeline.append({"$sort": {"total_engagement": -1}})
        
        return list(db.posts.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 3. Most Popular Posts
# ===========================================================================

def get_top_posts(limit=10, category=None):
    """
    Returns top-N posts ranked by total engagement.

    total_engagement = likes + shares + comment_count

    Uses $lookup to fetch comment count per post, $project, $sort, $limit.

    Args:
        limit (int): Number of top posts to return. Default 10.
        category (str, optional): Filter to a specific category. If None, returns all categories.

    Returns:
        list[dict]: top posts with engagement metrics.
    """
    db, client = _get_db()
    try:
        pipeline = []
        
        # Add category filter if specified
        if category is not None:
            pipeline.append({"$match": {"category": category}})
        
        # Join comments to get comment count per post
        pipeline.append({
            "$lookup": {
                "from": "comments",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "post_comments"
            }
        })
        pipeline.append({
            "$project": {
                "_id": 0,
                "post_id": 1,
                "user_id": 1,
                "category": 1,
                "content": 1,
                "views": 1,
                "likes": 1,
                "shares": 1,
                "timestamp": 1,
                "comment_count": {"$size": "$post_comments"},
                "total_engagement": {
                    "$add": [
                        "$likes",
                        "$shares",
                        {"$size": "$post_comments"}
                    ]
                }
            }
        })
        pipeline.append({"$sort": {"total_engagement": -1}})
        pipeline.append({"$limit": limit})
        
        return list(db.posts.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 4. Most Active Users
# ===========================================================================

def get_top_users(limit=10):
    """
    Returns top-N users ranked by total number of interactions performed.

    Groups interaction events per user, then enriches with user profile.
    Includes per-type breakdowns: views, likes, shares, comments.

    Uses $group, $lookup, $project, $sort, $limit.

    Args:
        limit (int): Number of top users to return. Default 10.

    Returns:
        list[dict]: top users with interaction counts and profile info.
    """
    db, client = _get_db()
    try:
        pipeline = [
            # Step 1: Group interactions per user, count totals and per type
            {
                "$group": {
                    "_id": "$user_id",
                    "total_interactions": {"$sum": 1},
                    "total_likes": {
                        "$sum": {"$cond": [{"$eq": ["$interaction_type", "like"]}, 1, 0]}
                    },
                    "total_shares": {
                        "$sum": {"$cond": [{"$eq": ["$interaction_type", "share"]}, 1, 0]}
                    },
                    "total_views": {
                        "$sum": {"$cond": [{"$eq": ["$interaction_type", "view"]}, 1, 0]}
                    },
                    "total_comments": {
                        "$sum": {"$cond": [{"$eq": ["$interaction_type", "comment"]}, 1, 0]}
                    }
                }
            },
            {"$sort": {"total_interactions": -1}},
            {"$limit": limit},
            # Step 2: Enrich with user profile
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "_id": 0,
                    "user_id": "$_id",
                    "username": "$user_info.username",
                    "location": "$user_info.location",
                    "followers": "$user_info.followers",
                    "total_interactions": 1,
                    "total_likes": 1,
                    "total_shares": 1,
                    "total_views": 1,
                    "total_comments": 1
                }
            }
        ]
        return list(db.interactions.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 5. Activity Over Time
# ===========================================================================

def get_activity_over_time(granularity="day"):
    """
    Groups interaction events by time period (day or month).

    Uses MongoDB $dateToString to extract the date portion from
    the BSON datetime timestamp.

    Args:
        granularity (str): 'day' or 'month'. Default 'day'.

    Returns:
        list[dict]: list of {period, interaction_count} sorted chronologically.
    """
    db, client = _get_db()
    try:
        if granularity == "month":
            date_fmt = "%Y-%m"
        else:
            date_fmt = "%Y-%m-%d"

        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": date_fmt,
                            "date": "$timestamp"
                        }
                    },
                    "interaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "period": "$_id",
                    "interaction_count": 1
                }
            }
        ]
        return list(db.interactions.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 6. Interaction Type Distribution
# ===========================================================================

def get_interaction_type_distribution():
    """
    Counts interaction events grouped by interaction_type.

    Expected types: like, share, view, comment.

    Uses $group, $sort.

    Returns:
        list[dict]: list of {interaction_type, count} sorted by count desc.
    """
    db, client = _get_db()
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$interaction_type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {
                "$project": {
                    "_id": 0,
                    "interaction_type": "$_id",
                    "count": 1
                }
            }
        ]
        return list(db.interactions.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 7. Top Hashtags
# ===========================================================================

def get_top_hashtags(limit=10, category=None):
    """
    Unwinds the hashtags array on each post document and groups by hashtag
    to find the most frequently used tags.

    Uses $unwind, $group, $sort, $limit — demonstrating array unwinding
    as a key MongoDB aggregation capability.

    Args:
        limit (int): Number of top hashtags to return. Default 10.
        category (str, optional): Filter to a specific category. If None, returns all categories.

    Returns:
        list[dict]: list of {hashtag, usage_count} sorted by usage_count desc.
    """
    db, client = _get_db()
    try:
        pipeline = []
        
        # Add category filter if specified
        if category is not None:
            pipeline.append({"$match": {"category": category}})
        
        # Unwind flattens the array — one document per hashtag
        pipeline.append({"$unwind": "$hashtags"})
        pipeline.append({
            "$group": {
                "_id": "$hashtags",
                "usage_count": {"$sum": 1}
            }
        })
        pipeline.append({"$sort": {"usage_count": -1}})
        pipeline.append({"$limit": limit})
        pipeline.append({
            "$project": {
                "_id": 0,
                "hashtag": "$_id",
                "usage_count": 1
            }
        })
        
        return list(db.posts.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 8. Sentiment Distribution
# ===========================================================================

def get_sentiment_distribution(sentiment=None, category=None):
    """
    Counts comments grouped by sentiment label.

    Expected sentiments: Positive, Neutral, Negative.

    Uses $group, $sort on the comments collection.

    Args:
        sentiment (str, optional): Filter to a specific sentiment. If None, returns all sentiments.
        category (str, optional): Filter to a specific category. If None, returns all categories.

    Returns:
        list[dict]: list of {sentiment, comment_count} sorted by count desc.
    """
    db, client = _get_db()
    try:
        pipeline = []
        
        # Build match conditions
        match_conditions = {}
        if sentiment is not None:
            match_conditions["sentiment"] = sentiment
        
        # If category filter is specified, we need to join with posts first
        if category is not None:
            pipeline.append({
                "$lookup": {
                    "from": "posts",
                    "localField": "post_id",
                    "foreignField": "post_id",
                    "as": "post_info"
                }
            })
            pipeline.append({"$unwind": "$post_info"})
            match_conditions["post_info.category"] = category
        
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        pipeline.append({
            "$group": {
                "_id": "$sentiment",
                "comment_count": {"$sum": 1}
            }
        })
        pipeline.append({"$sort": {"comment_count": -1}})
        pipeline.append({
            "$project": {
                "_id": 0,
                "sentiment": "$_id",
                "comment_count": 1
            }
        })
        
        return list(db.comments.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 9. Sentiment by Category
# ===========================================================================

def get_sentiment_by_category(category=None, sentiment=None):
    """
    For each combination of (category, sentiment), counts the number of comments.

    Pipeline:
        comments -> $lookup posts -> $unwind -> $group by (category, sentiment)

    Uses $lookup, $unwind, $group, $project, $sort.

    Args:
        category (str, optional): Filter to a specific category. If None, returns all categories.
        sentiment (str, optional): Filter to a specific sentiment. If None, returns all sentiments.

    Returns:
        list[dict]: list of {category, sentiment, comment_count}
                    sorted by category then sentiment.
    """
    db, client = _get_db()
    try:
        pipeline = []
        
        # Build match conditions
        match_conditions = {}
        if sentiment is not None:
            match_conditions["sentiment"] = sentiment
        
        # Join each comment with its parent post to get category
        pipeline.append({
            "$lookup": {
                "from": "posts",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "post_info"
            }
        })
        pipeline.append({"$unwind": "$post_info"})
        
        if category is not None:
            match_conditions["post_info.category"] = category
        
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        # Group by (category, sentiment)
        pipeline.append({
            "$group": {
                "_id": {
                    "category": "$post_info.category",
                    "sentiment": "$sentiment"
                },
                "comment_count": {"$sum": 1}
            }
        })
        pipeline.append({
            "$project": {
                "_id": 0,
                "category": "$_id.category",
                "sentiment": "$_id.sentiment",
                "comment_count": 1
            }
        })
        pipeline.append({"$sort": {"category": 1, "sentiment": 1}})
        
        return list(db.comments.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 10. Location-wise Analytics
# ===========================================================================

def get_location_engagement():
    """
    For each city location, computes the number of users, total interactions
    performed by those users, and total posts authored by those users.

    Pipeline:
        users -> group count per location
        users -> $lookup interactions -> $group
        users -> $lookup posts -> $group
        Merge via separate pipelines for clarity.

    Uses $lookup, $group, $project, $sort.

    Returns:
        list[dict]: {location, user_count, total_interactions, total_posts}
                    sorted by total_interactions desc.
    """
    db, client = _get_db()
    try:
        pipeline = [
            # Bring in interactions for each user
            {
                "$lookup": {
                    "from": "interactions",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_interactions"
                }
            },
            # Bring in posts for each user
            {
                "$lookup": {
                    "from": "posts",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_posts"
                }
            },
            # Group by location
            {
                "$group": {
                    "_id": "$location",
                    "user_count": {"$sum": 1},
                    "total_interactions": {
                        "$sum": {"$size": "$user_interactions"}
                    },
                    "total_posts": {
                        "$sum": {"$size": "$user_posts"}
                    }
                }
            },
            {"$sort": {"total_interactions": -1}},
            {
                "$project": {
                    "_id": 0,
                    "location": "$_id",
                    "user_count": 1,
                    "total_interactions": 1,
                    "total_posts": 1
                }
            }
        ]
        return list(db.users.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()


# ===========================================================================
# 11. Peak Interaction Hours
# ===========================================================================

def get_peak_interaction_hours():
    """
    Groups interaction events by the hour of day (0-23) extracted from
    the BSON datetime timestamp using the $hour date operator.

    Returns results sorted chronologically by hour ascending — suitable
    for a 24-hour activity line or bar chart.

    Uses $hour, $group, $project, $sort.

    Returns:
        list[dict]: list of {hour, interaction_count} for hours 0-23.
    """
    db, client = _get_db()
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {"$hour": "$timestamp"},
                    "interaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "hour": "$_id",
                    "interaction_count": 1
                }
            }
        ]
        return list(db.interactions.aggregate(pipeline))
    except Exception:
        return []
    finally:
        client.close()
