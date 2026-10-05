"""
MongoDB Data Ingestion Script
Phase 3: Schema Modeling and Data Ingestion

Reads CSV datasets from data/, transforms fields into appropriate BSON types,
creates collections, creates indexes, and safely populates MongoDB.
"""

import os
import sys
from datetime import datetime
import pandas as pd
from pymongo import ASCENDING

# Ensure script directory is on sys.path for direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from connection import get_database

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_data_dir():
    """Returns absolute path to the data directory."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "data")


def parse_hashtags(hashtag_str):
    """Converts serialized hashtag string into a clean list of hashtag strings."""
    if not isinstance(hashtag_str, str) or not hashtag_str.strip():
        return []
    # Support both space-separated and comma-separated formats
    raw_tags = hashtag_str.replace(",", " ").split()
    return [tag.strip() for tag in raw_tags if tag.strip()]


def parse_date(date_val, fmt=None):
    """Parses date string or pandas Timestamp into a standard Python datetime object."""
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, pd.Timestamp):
        return date_val.to_pydatetime()
    date_str = str(date_val).strip()
    if fmt:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    for f in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, f)
        except ValueError:
            continue
    return pd.to_datetime(date_str, format="mixed").to_pydatetime()


def ingest_users(db, data_dir):
    """Loads users.csv, transforms types, and inserts into users collection."""
    print("[1/4] Ingesting Users...")
    csv_path = os.path.join(data_dir, "users.csv")
    df = pd.read_csv(csv_path)

    records = []
    for _, row in df.iterrows():
        record = {
            "user_id": str(row["user_id"]).strip(),
            "username": str(row["username"]).strip(),
            "age": int(row["age"]),
            "gender": str(row["gender"]).strip(),
            "location": str(row["location"]).strip(),
            "followers": int(row["followers"]),
            "following": int(row["following"]),
            "join_date": parse_date(row["join_date"], "%Y-%m-%d")
        }
        records.append(record)

    db.users.delete_many({})
    db.users.insert_many(records)
    print(f"      Inserted {len(records):,} documents into 'users'.")


def ingest_posts(db, data_dir):
    """Loads posts.csv, transforms types and hashtags array, and inserts into posts collection."""
    print("[2/4] Ingesting Posts...")
    csv_path = os.path.join(data_dir, "posts.csv")
    df = pd.read_csv(csv_path)

    records = []
    for _, row in df.iterrows():
        record = {
            "post_id": str(row["post_id"]).strip(),
            "user_id": str(row["user_id"]).strip(),
            "content": str(row["content"]).strip(),
            "category": str(row["category"]).strip(),
            "hashtags": parse_hashtags(row["hashtags"]),
            "timestamp": parse_date(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
            "likes": int(row["likes"]),
            "shares": int(row["shares"]),
            "views": int(row["views"])
        }
        records.append(record)

    db.posts.delete_many({})
    db.posts.insert_many(records)
    print(f"      Inserted {len(records):,} documents into 'posts'.")


def ingest_comments(db, data_dir):
    """Loads comments.csv, transforms types, and inserts into comments collection."""
    print("[3/4] Ingesting Comments...")
    csv_path = os.path.join(data_dir, "comments.csv")
    df = pd.read_csv(csv_path)

    records = []
    for _, row in df.iterrows():
        record = {
            "comment_id": str(row["comment_id"]).strip(),
            "post_id": str(row["post_id"]).strip(),
            "user_id": str(row["user_id"]).strip(),
            "comment_text": str(row["comment_text"]).strip(),
            "timestamp": parse_date(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
            "sentiment": str(row["sentiment"]).strip()
        }
        records.append(record)

    db.comments.delete_many({})
    db.comments.insert_many(records)
    print(f"      Inserted {len(records):,} documents into 'comments'.")


def ingest_interactions(db, data_dir):
    """Loads interactions.csv, transforms types, and inserts into interactions collection."""
    print("[4/4] Ingesting Interactions...")
    csv_path = os.path.join(data_dir, "interactions.csv")
    df = pd.read_csv(csv_path)

    records = []
    for _, row in df.iterrows():
        record = {
            "interaction_id": str(row["interaction_id"]).strip(),
            "user_id": str(row["user_id"]).strip(),
            "post_id": str(row["post_id"]).strip(),
            "interaction_type": str(row["interaction_type"]).strip(),
            "timestamp": parse_date(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        }
        records.append(record)

    db.interactions.delete_many({})
    db.interactions.insert_many(records)
    print(f"      Inserted {len(records):,} documents into 'interactions'.")


def create_indexes(db):
    """Creates single-field and unique indexes for future analytical performance."""
    print("\nCreating indexes...")

    # Users Indexes
    db.users.create_index([("user_id", ASCENDING)], unique=True, name="idx_user_id_unique")

    # Posts Indexes
    db.posts.create_index([("post_id", ASCENDING)], unique=True, name="idx_post_id_unique")
    db.posts.create_index([("user_id", ASCENDING)], name="idx_posts_user_id")
    db.posts.create_index([("category", ASCENDING)], name="idx_posts_category")
    db.posts.create_index([("timestamp", ASCENDING)], name="idx_posts_timestamp")

    # Comments Indexes
    db.comments.create_index([("comment_id", ASCENDING)], unique=True, name="idx_comment_id_unique")
    db.comments.create_index([("post_id", ASCENDING)], name="idx_comments_post_id")
    db.comments.create_index([("user_id", ASCENDING)], name="idx_comments_user_id")
    db.comments.create_index([("timestamp", ASCENDING)], name="idx_comments_timestamp")

    # Interactions Indexes
    db.interactions.create_index([("interaction_id", ASCENDING)], unique=True, name="idx_interaction_id_unique")
    db.interactions.create_index([("user_id", ASCENDING)], name="idx_interactions_user_id")
    db.interactions.create_index([("post_id", ASCENDING)], name="idx_interactions_post_id")
    db.interactions.create_index([("interaction_type", ASCENDING)], name="idx_interactions_type")
    db.interactions.create_index([("timestamp", ASCENDING)], name="idx_interactions_timestamp")

    print("Indexes created successfully.")


def main():
    print("=" * 60)
    print("MongoDB-Based Social Media Analytics — Phase 3 Ingestion")
    print("=" * 60)

    try:
        db, client = get_database()
        print(f"Connected to MongoDB database: '{db.name}'\n")

        data_dir = get_data_dir()
        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"Data directory '{data_dir}' not found.")

        # Ingest datasets
        ingest_users(db, data_dir)
        ingest_posts(db, data_dir)
        ingest_comments(db, data_dir)
        ingest_interactions(db, data_dir)

        # Create indexes
        create_indexes(db)

        print("\nIngestion and index creation complete!")
        print("=" * 60)
        client.close()
    except Exception as err:
        print(f"\n[FATAL] Ingestion failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
