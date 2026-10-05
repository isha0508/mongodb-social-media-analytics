"""
Dashboard Logic Test Script
Phase 6: Integration, Filtering, Testing & Final Polish

Tests the underlying functions used by the dashboard with filter parameters.
Ensures backward compatibility and correct filter behavior.
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
    get_category_engagement,
    get_top_posts,
    get_top_hashtags,
    get_sentiment_distribution,
    get_sentiment_by_category
)

PASS = "PASS"
FAIL = "FAIL"

results = {}


def test_backward_compatibility():
    """Test that all functions work without filter parameters (backward compatibility)."""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    
    passed = True
    
    # Test get_category_engagement without parameters
    try:
        result = get_category_engagement()
        assert isinstance(result, list), "Should return a list"
        assert len(result) > 0, "Should return at least one category"
        print("✓ get_category_engagement() - PASS")
    except Exception as e:
        print(f"✗ get_category_engagement() - FAIL: {e}")
        passed = False
    
    # Test get_top_posts without category parameter
    try:
        result = get_top_posts(limit=10)
        assert isinstance(result, list), "Should return a list"
        assert len(result) <= 10, "Should respect limit"
        print("✓ get_top_posts(limit=10) - PASS")
    except Exception as e:
        print(f"✗ get_top_posts(limit=10) - FAIL: {e}")
        passed = False
    
    # Test get_top_hashtags without category parameter
    try:
        result = get_top_hashtags(limit=10)
        assert isinstance(result, list), "Should return a list"
        assert len(result) <= 10, "Should respect limit"
        print("✓ get_top_hashtags(limit=10) - PASS")
    except Exception as e:
        print(f"✗ get_top_hashtags(limit=10) - FAIL: {e}")
        passed = False
    
    # Test get_sentiment_distribution without parameters
    try:
        result = get_sentiment_distribution()
        assert isinstance(result, list), "Should return a list"
        assert len(result) > 0, "Should return at least one sentiment"
        print("✓ get_sentiment_distribution() - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_distribution() - FAIL: {e}")
        passed = False
    
    # Test get_sentiment_by_category without parameters
    try:
        result = get_sentiment_by_category()
        assert isinstance(result, list), "Should return a list"
        assert len(result) > 0, "Should return at least one category-sentiment combination"
        print("✓ get_sentiment_by_category() - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_by_category() - FAIL: {e}")
        passed = False
    
    results["Backward Compatibility"] = passed
    return passed


def test_category_filter():
    """Test category filter functionality."""
    print("\n" + "=" * 60)
    print("Testing Category Filter")
    print("=" * 60)
    
    passed = True
    
    # Test get_category_engagement with category filter
    try:
        result = get_category_engagement(category="Technology")
        assert isinstance(result, list), "Should return a list"
        if len(result) > 0:
            assert result[0].get("category") == "Technology", "Should filter to Technology"
        print("✓ get_category_engagement(category='Technology') - PASS")
    except Exception as e:
        print(f"✗ get_category_engagement(category='Technology') - FAIL: {e}")
        passed = False
    
    # Test get_top_posts with category filter
    try:
        result = get_top_posts(limit=10, category="Technology")
        assert isinstance(result, list), "Should return a list"
        assert len(result) <= 10, "Should respect limit"
        if len(result) > 0:
            for post in result:
                assert post.get("category") == "Technology", "All posts should be Technology"
        print("✓ get_top_posts(limit=10, category='Technology') - PASS")
    except Exception as e:
        print(f"✗ get_top_posts(limit=10, category='Technology') - FAIL: {e}")
        passed = False
    
    # Test get_top_hashtags with category filter
    try:
        result = get_top_hashtags(limit=10, category="Technology")
        assert isinstance(result, list), "Should return a list"
        assert len(result) <= 10, "Should respect limit"
        print("✓ get_top_hashtags(limit=10, category='Technology') - PASS")
    except Exception as e:
        print(f"✗ get_top_hashtags(limit=10, category='Technology') - FAIL: {e}")
        passed = False
    
    results["Category Filter"] = passed
    return passed


def test_sentiment_filter():
    """Test sentiment filter functionality."""
    print("\n" + "=" * 60)
    print("Testing Sentiment Filter")
    print("=" * 60)
    
    passed = True
    
    # Test get_sentiment_distribution with sentiment filter
    try:
        result = get_sentiment_distribution(sentiment="Positive")
        assert isinstance(result, list), "Should return a list"
        if len(result) > 0:
            assert result[0].get("sentiment") == "Positive", "Should filter to Positive"
        print("✓ get_sentiment_distribution(sentiment='Positive') - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_distribution(sentiment='Positive') - FAIL: {e}")
        passed = False
    
    # Test get_sentiment_by_category with sentiment filter
    try:
        result = get_sentiment_by_category(sentiment="Positive")
        assert isinstance(result, list), "Should return a list"
        if len(result) > 0:
            for item in result:
                assert item.get("sentiment") == "Positive", "All items should be Positive"
        print("✓ get_sentiment_by_category(sentiment='Positive') - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_by_category(sentiment='Positive') - FAIL: {e}")
        passed = False
    
    results["Sentiment Filter"] = passed
    return passed


def test_combined_filters():
    """Test combined category and sentiment filters."""
    print("\n" + "=" * 60)
    print("Testing Combined Filters")
    print("=" * 60)
    
    passed = True
    
    # Test get_sentiment_distribution with both filters
    try:
        result = get_sentiment_distribution(sentiment="Positive", category="Technology")
        assert isinstance(result, list), "Should return a list"
        print("✓ get_sentiment_distribution(sentiment='Positive', category='Technology') - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_distribution(sentiment='Positive', category='Technology') - FAIL: {e}")
        passed = False
    
    # Test get_sentiment_by_category with both filters
    try:
        result = get_sentiment_by_category(category="Technology", sentiment="Positive")
        assert isinstance(result, list), "Should return a list"
        if len(result) > 0:
            for item in result:
                assert item.get("category") == "Technology", "Should be Technology"
                assert item.get("sentiment") == "Positive", "Should be Positive"
        print("✓ get_sentiment_by_category(category='Technology', sentiment='Positive') - PASS")
    except Exception as e:
        print(f"✗ get_sentiment_by_category(category='Technology', sentiment='Positive') - FAIL: {e}")
        passed = False
    
    results["Combined Filters"] = passed
    return passed


def test_empty_result_handling():
    """Test that functions handle empty results gracefully."""
    print("\n" + "=" * 60)
    print("Testing Empty Result Handling")
    print("=" * 60)
    
    passed = True
    
    # Test with a non-existent category
    try:
        result = get_category_engagement(category="NonExistentCategory")
        assert isinstance(result, list), "Should return a list even if empty"
        assert len(result) == 0, "Should return empty list for non-existent category"
        print("✓ get_category_engagement(category='NonExistentCategory') - PASS (empty list)")
    except Exception as e:
        print(f"✗ get_category_engagement(category='NonExistentCategory') - FAIL: {e}")
        passed = False
    
    # Test with a non-existent sentiment
    try:
        result = get_sentiment_distribution(sentiment="NonExistentSentiment")
        assert isinstance(result, list), "Should return a list even if empty"
        assert len(result) == 0, "Should return empty list for non-existent sentiment"
        print("✓ get_sentiment_distribution(sentiment='NonExistentSentiment') - PASS (empty list)")
    except Exception as e:
        print(f"✗ get_sentiment_distribution(sentiment='NonExistentSentiment') - FAIL: {e}")
        passed = False
    
    results["Empty Result Handling"] = passed
    return passed


def main():
    print("=" * 60)
    print("MongoDB-Based Social Media Analytics - Dashboard Logic Tests")
    print("=" * 60)
    
    # Run all tests
    test_backward_compatibility()
    test_category_filter()
    test_sentiment_filter()
    test_combined_filters()
    test_empty_result_handling()
    
    # Final summary
    print("\n" + "=" * 60)
    print("DASHBOARD LOGIC TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = PASS if passed else FAIL
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"\n  Result: {passed_count}/{total} test groups PASSED")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
