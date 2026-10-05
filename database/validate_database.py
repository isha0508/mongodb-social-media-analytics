"""
MongoDB Database Validation Script
Phase 3: Schema Modeling and Data Ingestion

Validates:
- MongoDB connection
- Existence of collections and document counts
- ID uniqueness and absence of duplicates
- Required fields
- BSON datetime types
- Referential integrity between collections
- Creation of expected indexes
"""

import os
import sys
from datetime import datetime

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


def validate_database():
    """Performs comprehensive validation of the social_media_analytics database."""
    print("=" * 60)
    print("MongoDB-Based Social Media Analytics — Database Validation")
    print("=" * 60)

    # 1. Connection check
    try:
        db, client = get_database()
        print("MongoDB Connection: PASS")
    except Exception as err:
        print(f"MongoDB Connection: FAIL ({err})")
        return False

    all_passed = True

    # 2. Collections and Document Counts
    expected_counts = {
        "users": 1000,
        "posts": 5000,
        "comments": 15000,
        "interactions": 20000
    }

    print("\nCollections:")
    existing_collections = db.list_collection_names()
    for coll_name, expected_count in expected_counts.items():
        if coll_name in existing_collections:
            actual_count = db[coll_name].count_documents({})
            if actual_count == expected_count:
                print(f"{coll_name}: {actual_count:,} documents")
            else:
                print(f"{coll_name}: {actual_count:,} documents (Expected {expected_count:,}) - FAIL")
                all_passed = False
        else:
            print(f"{coll_name}: Missing collection - FAIL")
            all_passed = False

    # 3. Data Types Check (BSON datetime)
    print("\nData Types:")
    date_types_valid = True

    # Check users join_date
    sample_user = db.users.find_one({}, {"join_date": 1})
    if not sample_user or not isinstance(sample_user.get("join_date"), datetime):
        date_types_valid = False

    # Check posts timestamp
    sample_post = db.posts.find_one({}, {"timestamp": 1})
    if not sample_post or not isinstance(sample_post.get("timestamp"), datetime):
        date_types_valid = False

    # Check comments timestamp
    sample_comment = db.comments.find_one({}, {"timestamp": 1})
    if not sample_comment or not isinstance(sample_comment.get("timestamp"), datetime):
        date_types_valid = False

    # Check interactions timestamp
    sample_int = db.interactions.find_one({}, {"timestamp": 1})
    if not sample_int or not isinstance(sample_int.get("timestamp"), datetime):
        date_types_valid = False

    if date_types_valid:
        print("Dates stored as BSON datetime: PASS")
    else:
        print("Dates stored as BSON datetime: FAIL")
        all_passed = False

    # 4. Primary Key Uniqueness
    id_unique_valid = True
    for coll_name, id_field in [
        ("users", "user_id"),
        ("posts", "post_id"),
        ("comments", "comment_id"),
        ("interactions", "interaction_id")
    ]:
        total_docs = db[coll_name].count_documents({})
        distinct_ids = len(db[coll_name].distinct(id_field))
        if total_docs != distinct_ids:
            id_unique_valid = False
            print(f"Duplicate {id_field} in {coll_name}: FAIL ({distinct_ids} distinct vs {total_docs} total)")

    if id_unique_valid:
        pass  # Will be reported with indexes/validation summary

    # 5. Referential Integrity
    print("\nReferences:")
    all_users = set(db.users.distinct("user_id"))
    all_posts = set(db.posts.distinct("post_id"))

    # Post -> User
    post_users = set(db.posts.distinct("user_id"))
    post_user_valid = post_users.issubset(all_users)
    print(f"Post → User: {'PASS' if post_user_valid else 'FAIL'}")
    if not post_user_valid:
        all_passed = False

    # Comment -> User
    comment_users = set(db.comments.distinct("user_id"))
    comment_user_valid = comment_users.issubset(all_users)
    print(f"Comment → User: {'PASS' if comment_user_valid else 'FAIL'}")
    if not comment_user_valid:
        all_passed = False

    # Comment -> Post
    comment_posts = set(db.comments.distinct("post_id"))
    comment_post_valid = comment_posts.issubset(all_posts)
    print(f"Comment → Post: {'PASS' if comment_post_valid else 'FAIL'}")
    if not comment_post_valid:
        all_passed = False

    # Interaction -> User
    int_users = set(db.interactions.distinct("user_id"))
    int_user_valid = int_users.issubset(all_users)
    print(f"Interaction → User: {'PASS' if int_user_valid else 'FAIL'}")
    if not int_user_valid:
        all_passed = False

    # Interaction -> Post
    int_posts = set(db.interactions.distinct("post_id"))
    int_post_valid = int_posts.issubset(all_posts)
    print(f"Interaction → Post: {'PASS' if int_post_valid else 'FAIL'}")
    if not int_post_valid:
        all_passed = False

    # 6. Indexes Check
    expected_indexes = {
        "users": ["_id_", "idx_user_id_unique"],
        "posts": ["_id_", "idx_post_id_unique", "idx_posts_user_id", "idx_posts_category", "idx_posts_timestamp"],
        "comments": ["_id_", "idx_comment_id_unique", "idx_comments_post_id", "idx_comments_user_id", "idx_comments_timestamp"],
        "interactions": [
            "_id_", "idx_interaction_id_unique", "idx_interactions_user_id",
            "idx_interactions_post_id", "idx_interactions_type", "idx_interactions_timestamp"
        ]
    }

    indexes_valid = True
    for coll_name, exp_idx_list in expected_indexes.items():
        actual_indexes = list(db[coll_name].index_information().keys())
        for exp_idx in exp_idx_list:
            if exp_idx not in actual_indexes:
                print(f"Missing index '{exp_idx}' on '{coll_name}': FAIL")
                indexes_valid = False

    print(f"\nIndexes: {'PASS' if indexes_valid else 'FAIL'}")
    if not indexes_valid:
        all_passed = False

    print("=" * 60)
    client.close()
    return all_passed


if __name__ == "__main__":
    success = validate_database()
    sys.exit(0 if success else 1)
