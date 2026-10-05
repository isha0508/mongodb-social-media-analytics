# Analytics Summary

Quick-reference table for all analytical functions implemented in Phase 4.

Each function is implemented in [`analytics/aggregation_queries.py`](aggregation_queries.py) and tested in [`analytics/test_analytics.py`](test_analytics.py). Full documentation is in [`analytics/ANALYTICS_DOCUMENTATION.md`](ANALYTICS_DOCUMENTATION.md).

---

## Analysis Summary Table

| # | Analysis | Function | Collection(s) | Main MongoDB Operations | Future Visualization |
|---|---|---|---|---|---|
| 1 | Overview Metrics | `get_overview_metrics()` | users / posts / comments / interactions | `count_documents`, `$group`, `$sum` | KPI cards |
| 2 | Category Engagement | `get_category_engagement()` | posts / comments | `$lookup`, `$project`, `$group`, `$sort` | Bar chart |
| 3 | Top Posts | `get_top_posts(limit)` | posts / comments | `$lookup`, `$project`, `$sort`, `$limit` | Ranked table |
| 4 | Top Active Users | `get_top_users(limit)` | interactions / users | `$group`, `$sort`, `$limit`, `$lookup`, `$unwind`, `$project` | Ranked table |
| 5 | Activity Over Time | `get_activity_over_time(granularity)` | interactions | `$dateToString`, `$group`, `$sort` | Line chart |
| 6 | Interaction Types | `get_interaction_type_distribution()` | interactions | `$group`, `$sort`, `$project` | Pie / bar chart |
| 7 | Top Hashtags | `get_top_hashtags(limit)` | posts | `$unwind`, `$group`, `$sort`, `$limit` | Bar chart |
| 8 | Sentiment Distribution | `get_sentiment_distribution()` | comments | `$group`, `$sort`, `$project` | Pie chart |
| 9 | Sentiment by Category | `get_sentiment_by_category()` | comments / posts | `$lookup`, `$unwind`, `$group`, `$project`, `$sort` | Stacked bar chart |
| 10 | Location Engagement | `get_location_engagement()` | users / interactions / posts | `$lookup`, `$group`, `$sort`, `$project` | Bar chart |
| 11 | Peak Interaction Hours | `get_peak_interaction_hours()` | interactions | `$hour`, `$group`, `$sort`, `$project` | Line / bar chart |

---

## MongoDB Aggregation Operators Demonstrated

| Operator | Used In |
|---|---|
| `$group` | All analyses |
| `$sum` | All analyses with counting/aggregation |
| `$sort` | All analyses |
| `$project` | All analyses |
| `$lookup` | Category Engagement, Top Posts, Top Users, Sentiment by Category, Location Engagement |
| `$unwind` | Top Users, Top Hashtags, Sentiment by Category |
| `$limit` | Top Posts, Top Users, Top Hashtags |
| `$cond` | Top Users (conditional per-type counting) |
| `$size` | Top Posts (comment array size) |
| `$add` | Category Engagement, Top Posts (engagement calculation) |
| `$dateToString` | Activity Over Time |
| `$hour` | Peak Interaction Hours |

---

## Running the Test Suite

```bash
python analytics/test_analytics.py
```

Expected output:
```text
Result: 12/12 analyses PASSED
```

---

## Importing Into Phase 5 Dashboard

All functions can be imported individually into `app.py`:

```python
from analytics.aggregation_queries import (
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
```
