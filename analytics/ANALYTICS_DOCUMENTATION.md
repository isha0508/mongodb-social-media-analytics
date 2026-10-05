# Analytics Documentation

This document describes every analytical function implemented in **Phase 4** of the **MongoDB-Based Social Media Analytics** project.

All analytical calculations are performed inside MongoDB using aggregation pipelines via PyMongo. Pandas is used only for formatting in the dashboard layer.

---

## 1. Overview Metrics

**Purpose:**
Provides high-level KPI summary values across all four collections: total users, posts, comments, interactions, and aggregate engagement counts (views, likes, shares). This is the first thing displayed on the dashboard.

**Collection(s) used:**
`users`, `posts`, `comments`, `interactions`

**MongoDB operations used:**
```
count_documents()
$group
$sum
```

**Calculation:**
- `total_users` — `users.count_documents({})`
- `total_posts` — `posts.count_documents({})`
- `total_comments` — `comments.count_documents({})`
- `total_interactions` — `interactions.count_documents({})`
- `total_views`, `total_likes`, `total_shares` — `$group` with `$sum` over all post documents

**Output:**
A single dictionary with seven numeric KPI values.

**Future visualization:**
7 dashboard KPI metric cards displayed at the top of the Streamlit page.

---

## 2. Category Engagement

**Purpose:**
Reveals which content categories generate the most user engagement. Helps identify the most popular topic types on the platform.

**Collection(s) used:**
`posts`, `comments`

**MongoDB operations used:**
```
$lookup
$project
$group
$sort
```

**Calculation:**
For each post, the number of associated comments is fetched via `$lookup`. Then all posts are grouped by `category`:
- `post_count` — count of posts in that category
- `total_views`, `total_likes`, `total_shares` — summed from post fields
- `total_comments` — summed comment counts per post
- `total_engagement` = `total_likes + total_shares + total_comments`

Results are sorted by `total_engagement` descending.

**Output:**
List of 10 records, one per category, with engagement metrics.

**Sample result:**
```
Fashion: engagement=145,450, posts=516, views=1,216,141, likes=133,521
Food:    engagement=128,855, posts=485, views=1,134,710, likes=118,112
```

**Future visualization:**
Grouped/stacked horizontal bar chart showing engagement per category.

---

## 3. Top Posts

**Purpose:**
Identifies the most engaging individual posts, enabling discovery of viral or high-performing content.

**Collection(s) used:**
`posts`, `comments`

**MongoDB operations used:**
```
$lookup
$project
$sort
$limit
```

**Calculation:**
Each post document is enriched with its comment count via `$lookup` on `comments.post_id`. Then:
- `comment_count` = `$size` of joined comments array
- `total_engagement` = `likes + shares + comment_count`

Sorted descending by `total_engagement`. Limited to `N` records.

**Output:**
List of top-N post documents with full engagement breakdown.

**Sample top post:**
```
POST_1825 (Business) — views: 60,000, likes: 10,537, shares: 1,238,
comments: 47, total_engagement: 11,822
```

**Future visualization:**
Sortable ranked data table with columns for post, category, views, likes, shares, comments, engagement.

---

## 4. Top Active Users

**Purpose:**
Identifies the most active platform participants based on their total interaction events (views, likes, shares, comments recorded in the interactions collection).

**Collection(s) used:**
`interactions`, `users`

**MongoDB operations used:**
```
$group
$sort
$limit
$lookup
$unwind
$project
```

**Calculation:**
The `interactions` collection is grouped by `user_id`. For each user:
- `total_interactions` — total event count
- `total_likes`, `total_shares`, `total_views`, `total_comments` — counted using `$cond` conditional sums

After sorting and limiting, user profile data (username, location, followers) is joined via `$lookup` on `users.user_id`.

**Output:**
List of top-N users with interaction breakdowns and profile metadata.

**Future visualization:**
Ranked table showing username, location, followers, and interaction breakdown.

---

## 5. Activity Over Time

**Purpose:**
Shows the temporal distribution of interaction events — reveals platform activity peaks, growth trends, and seasonal patterns across the 12-month dataset period.

**Collection(s) used:**
`interactions`

**MongoDB operations used:**
```
$dateToString
$group
$sort
$project
```

**Calculation:**
The BSON `timestamp` field on each interaction is formatted using `$dateToString` with either `"%Y-%m-%d"` (day granularity) or `"%Y-%m"` (month granularity). Events are then grouped by this formatted period string and counted.

Supports `granularity="day"` or `granularity="month"` parameter.

**Output:**
List of `{period, interaction_count}` records sorted chronologically ascending.

**Sample (monthly):**
```
2025-10 → 1,832 interactions
2025-11 → 1,758 interactions
...
2026-09 → 1,945 interactions
```

**Future visualization:**
Line chart with date on x-axis and interaction count on y-axis.

---

## 6. Interaction Type Distribution

**Purpose:**
Shows the breakdown of engagement types (views, likes, shares, comments). Reveals the typical engagement funnel: most users view, fewer like, fewer still share or comment.

**Collection(s) used:**
`interactions`

**MongoDB operations used:**
```
$group
$sort
$project
```

**Calculation:**
All interaction records are grouped by `interaction_type` and counted. Sorted by count descending.

**Output:**
```
view:    11,005
like:     5,614
comment:  1,982
share:    1,399
```

**Future visualization:**
Pie chart or horizontal bar chart showing each interaction type's share.

---

## 7. Top Hashtags

**Purpose:**
Identifies the most frequently used hashtags across all posts, enabling trend analysis and content tagging insights. Demonstrates MongoDB's `$unwind` operator on array fields.

**Collection(s) used:**
`posts`

**MongoDB operations used:**
```
$unwind
$group
$sort
$limit
$project
```

**Calculation:**
The `hashtags` array field on each post document is flattened using `$unwind`, producing one document per hashtag. Documents are then grouped by the hashtag string and counted.

**Output:**
List of top-N `{hashtag, usage_count}` records sorted by usage_count descending.

**Sample:**
```
#Students:       326 uses
#Sustainability: 325 uses
#GoGreen:        324 uses
```

**Future visualization:**
Horizontal bar chart with hashtags on y-axis and usage count on x-axis.

---

## 8. Sentiment Distribution

**Purpose:**
Provides an overall view of community tone across all comments on the platform. Shows the proportion of Positive, Neutral, and Negative user responses.

**Collection(s) used:**
`comments`

**MongoDB operations used:**
```
$group
$sort
$project
```

**Calculation:**
All comment documents are grouped by the `sentiment` label and counted. Sorted by count descending.

**Output:**
```
Positive: 5,656 comments (37.7%)
Neutral:  5,010 comments (33.4%)
Negative: 4,334 comments (28.9%)
```

**Future visualization:**
Pie/donut chart with three segments.

---

## 9. Sentiment by Category

**Purpose:**
Breaks down comment sentiment for each post category — revealing which content types attract more positive vs. negative audience reactions.

**Collection(s) used:**
`comments`, `posts`

**MongoDB operations used:**
```
$lookup
$unwind
$group
$project
$sort
```

**Calculation:**
Each comment is joined with its parent post via `$lookup` on `post_id` to retrieve the post `category`. The combined records are then grouped by `(category, sentiment)` pair and counted. Results in 30 rows (10 categories × 3 sentiments).

**Output:**
List of `{category, sentiment, comment_count}` records sorted by category and sentiment.

**Future visualization:**
Grouped or stacked bar chart — one bar group per category, colored by sentiment.

---

## 10. Location-wise Engagement

**Purpose:**
Compares user activity across 10 Indian cities, showing which cities have the most active user bases, generate the most posts, and record the most interactions.

**Collection(s) used:**
`users`, `interactions`, `posts`

**MongoDB operations used:**
```
$lookup
$group
$sort
$project
```

**Calculation:**
For each user, their complete interaction list and post list are joined via `$lookup`. Users are then grouped by `location`:
- `user_count` — total users in that city
- `total_interactions` — sum of interaction counts across all city users
- `total_posts` — sum of post counts across all city users

Sorted by `total_interactions` descending.

**Output:**
```
Jaipur:    users=112, interactions=2,285, posts=589
Kolkata:   users=111, interactions=2,235, posts=549
Nashik:    users=103, interactions=2,072, posts=534
```

**Future visualization:**
Horizontal bar chart comparing cities by interaction volume.

---

## 11. Peak Interaction Hours

**Purpose:**
Reveals which hours of the day see the highest user activity — useful for understanding engagement patterns and optimal content posting times.

**Collection(s) used:**
`interactions`

**MongoDB operations used:**
```
$hour
$group
$sort
$project
```

**Calculation:**
The `$hour` MongoDB date expression extracts the hour (0–23) from the BSON datetime `timestamp` on each interaction. Documents are grouped by this hour value and counted. Results are sorted ascending by hour.

**Output:**
24 records, one per hour:
```
Hour 0 → 869 interactions
Hour 1 → 830 interactions
...
Hour 23 → N interactions
```

**Future visualization:**
Bar chart or line chart with hours (0–23) on x-axis and interaction count on y-axis.
