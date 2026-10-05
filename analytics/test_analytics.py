"""
Analytics Test Script
Phase 4: MongoDB Aggregation Pipelines & Analytics

Runs every analytical function, prints sample results, and reports PASS/FAIL.
Exits with code 0 if all tests pass, code 1 if any test fails.
"""

import os
import sys

# Ensure analytics/ and database/ directories are importable
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_analytics_dir = os.path.join(_project_root, "analytics")
_database_dir = os.path.join(_project_root, "database")
for _d in [_analytics_dir, _database_dir]:
    if _d not in sys.path:
        sys.path.insert(0, _d)

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

PASS = "PASS"
FAIL = "FAIL"

results = {}  # analysis_name -> bool


def check(name, result, expected_keys=None, min_records=1, max_display=5):
    """
    Validates a single analysis result and prints sample output.

    Args:
        name (str): Analysis display name.
        result: The returned data (list or dict).
        expected_keys (list): Required keys in each result record.
        min_records (int): Minimum expected records.
        max_display (int): Maximum sample records to print.
    """
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")

    passed = True

    if result is None:
        print("[FAIL] Result is None.")
        results[name] = False
        return

    if isinstance(result, dict):
        # Overview metrics special case
        if not result:
            print("[FAIL] Empty dict returned.")
            passed = False
        else:
            for k, v in result.items():
                print(f"  {k}: {v:,}")
            if expected_keys:
                for key in expected_keys:
                    if key not in result:
                        print(f"[FAIL] Missing key: '{key}'")
                        passed = False
    elif isinstance(result, list):
        count = len(result)
        print(f"  Records returned: {count}")
        if count < min_records:
            print(f"[FAIL] Expected at least {min_records} record(s), got {count}.")
            passed = False

        if count > 0 and expected_keys:
            for key in expected_keys:
                if key not in result[0]:
                    print(f"[FAIL] Missing key '{key}' in first record.")
                    passed = False

        # Print sample records
        for i, row in enumerate(result[:max_display]):
            print(f"  [{i + 1}] {row}")
        if count > max_display:
            print(f"  ... ({count - max_display} more records not shown)")

    status = PASS if passed else FAIL
    results[name] = passed
    print(f"\n  Status: {status}")


def main():
    print("=" * 60)
    print("MongoDB-Based Social Media Analytics - Phase 4 Test Suite")
    print("=" * 60)

    # 1. Overview Metrics
    check(
        "1. Overview Metrics",
        get_overview_metrics(),
        expected_keys=[
            "total_users", "total_posts", "total_comments",
            "total_interactions", "total_views", "total_likes", "total_shares"
        ]
    )

    # 2. Category Engagement
    check(
        "2. Category Engagement",
        get_category_engagement(),
        expected_keys=[
            "category", "post_count", "total_views",
            "total_likes", "total_shares", "total_comments", "total_engagement"
        ],
        min_records=1
    )

    # 3. Top Posts
    result_top_posts = get_top_posts(limit=10)
    check(
        "3. Top Posts (limit=10)",
        result_top_posts,
        expected_keys=[
            "post_id", "user_id", "category", "views",
            "likes", "shares", "comment_count", "total_engagement"
        ],
        min_records=1
    )
    # Verify limit is respected
    if len(result_top_posts) > 10:
        print("  [FAIL] Limit not respected: returned more than 10 records.")
        results["3. Top Posts (limit=10)"] = False

    # 4. Top Users
    result_top_users = get_top_users(limit=10)
    check(
        "4. Top Users (limit=10)",
        result_top_users,
        expected_keys=[
            "user_id", "username", "location",
            "followers", "total_interactions"
        ],
        min_records=1
    )

    # 5. Activity Over Time - Day
    result_day = get_activity_over_time(granularity="day")
    check(
        "5a. Activity Over Time (day)",
        result_day,
        expected_keys=["period", "interaction_count"],
        min_records=1
    )
    # Verify chronological order
    if len(result_day) >= 2:
        periods = [r["period"] for r in result_day]
        if periods != sorted(periods):
            print("  [FAIL] Daily activity not in chronological order.")
            results["5a. Activity Over Time (day)"] = False

    # 5. Activity Over Time - Month
    result_month = get_activity_over_time(granularity="month")
    check(
        "5b. Activity Over Time (month)",
        result_month,
        expected_keys=["period", "interaction_count"],
        min_records=1
    )

    # 6. Interaction Type Distribution
    result_types = get_interaction_type_distribution()
    check(
        "6. Interaction Type Distribution",
        result_types,
        expected_keys=["interaction_type", "count"],
        min_records=1
    )
    # Verify known types exist
    if result_types:
        known_types = {"like", "share", "view", "comment"}
        returned_types = {r["interaction_type"] for r in result_types}
        missing = known_types - returned_types
        if missing:
            print(f"  [WARN] Expected interaction types not found: {missing}")

    # 7. Top Hashtags
    result_hashtags = get_top_hashtags(limit=10)
    check(
        "7. Top Hashtags (limit=10)",
        result_hashtags,
        expected_keys=["hashtag", "usage_count"],
        min_records=1
    )
    if len(result_hashtags) > 10:
        print("  [FAIL] Hashtag limit not respected.")
        results["7. Top Hashtags (limit=10)"] = False

    # 8. Sentiment Distribution
    result_sentiment = get_sentiment_distribution()
    check(
        "8. Sentiment Distribution",
        result_sentiment,
        expected_keys=["sentiment", "comment_count"],
        min_records=1
    )
    if result_sentiment:
        returned_sentiments = {r["sentiment"] for r in result_sentiment}
        expected_sentiments = {"Positive", "Neutral", "Negative"}
        missing_s = expected_sentiments - returned_sentiments
        if missing_s:
            print(f"  [FAIL] Missing sentiments: {missing_s}")
            results["8. Sentiment Distribution"] = False

    # 9. Sentiment by Category
    check(
        "9. Sentiment by Category",
        get_sentiment_by_category(),
        expected_keys=["category", "sentiment", "comment_count"],
        min_records=1
    )

    # 10. Location Engagement
    check(
        "10. Location Engagement",
        get_location_engagement(),
        expected_keys=["location", "user_count", "total_interactions", "total_posts"],
        min_records=1
    )

    # 11. Peak Interaction Hours
    result_hours = get_peak_interaction_hours()
    check(
        "11. Peak Interaction Hours",
        result_hours,
        expected_keys=["hour", "interaction_count"],
        min_records=1
    )
    if result_hours:
        hours = [r["hour"] for r in result_hours]
        if hours != sorted(hours):
            print("  [FAIL] Hours not in ascending order.")
            results["11. Peak Interaction Hours"] = False
        for h in hours:
            if not (0 <= h <= 23):
                print(f"  [FAIL] Invalid hour value: {h}")
                results["11. Peak Interaction Hours"] = False

    # Final summary report
    print(f"\n{'=' * 60}")
    print("  ANALYTICS TEST SUMMARY")
    print(f"{'=' * 60}")
    all_passed = True
    for name, passed in results.items():
        status = PASS if passed else FAIL
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"\n  Result: {passed_count}/{total} analyses PASSED")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
