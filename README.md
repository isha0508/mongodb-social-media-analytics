# MongoDB-Based Social Media Analytics

An academic Big Data Analytics project designed to store and analyze social media data using MongoDB, Python, MongoDB aggregation pipelines, and Streamlit.

## Project Objective

The objective of this project is to model, store, and analyze social-media data—such as users, posts, comments, and user interactions—using NoSQL database technology (MongoDB) and provide interactive visual insights through a web dashboard.

## Phases

This project has successfully completed all planned phases:
- Phase 1: Project Setup
- Phase 2: Dataset Generation
- Phase 3: MongoDB Schema & Data Ingestion
- Phase 4: MongoDB Aggregation & Analytics
- Phase 5: Streamlit Dashboard
- Phase 6: Integration, Filtering, Testing & Final Polish

The application is fully functional with interactive filters, comprehensive testing, and is ready for academic demonstration.

## Technology Stack

- **Python 3.10+** (Core programming language)
- **MongoDB** (NoSQL document database, Community Edition 9.0+)
- **PyMongo** (MongoDB driver for Python)
- **Streamlit** (Interactive web application dashboard)
- **Pandas** (Data manipulation and structured representation)
- **Plotly** (Interactive data visualization charts)
- **python-dotenv** (Environment variable management)

## Project Structure

```
social-media-analytics/
│
├── app.py                          # Streamlit application entry point
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
├── .gitignore                      # Git exclusion rules
├── .env.example                    # Environment variable template
│
├── data/                           # Datasets and generator
│   ├── generate_dataset.py         # Deterministic dataset generation script
│   ├── DATASET_DESCRIPTION.md      # Detailed data dictionary
│   ├── users.csv                   # 1,000 user profiles
│   ├── posts.csv                   # 5,000 social media posts
│   ├── comments.csv                # 15,000 post comments
│   └── interactions.csv            # 20,000 engagement events
│
├── database/                       # MongoDB integration & schema modeling
│   ├── connection.py               # Reusable MongoDB connection provider
│   ├── ingest_data.py              # BSON type converter & collection loader
│   ├── validate_database.py        # Database integrity & index verification
│   └── MONGODB_SCHEMA.md           # Complete NoSQL schema documentation
│
├── analytics/                      # MongoDB aggregation analytics module
│   ├── aggregation_queries.py      # 11 reusable aggregation pipeline functions
│   ├── test_analytics.py           # Analytics test suite (12/12 PASS)
│   ├── ANALYTICS_DOCUMENTATION.md  # Detailed per-function documentation
│   └── ANALYTICS_SUMMARY.md        # Quick-reference operator & function table
│
├── utils/                          # Helper functions (.gitkeep)
└── assets/                         # Static assets like images/logos (.gitkeep)
```

## Phase 2 — Dataset

### Dataset Purpose
The dataset simulates realistic social-media user engagement and content trends across 10 major Indian cities and 10 content categories. It serves as the foundation for MongoDB schema modeling, indexing, document ingestion, and aggregation pipeline analytics.

### Datasets Summary

| Dataset | Records | File | Purpose |
|---|---|---|---|
| **Users** | 1,000 | `data/users.csv` | User accounts, demographics, follower/following counts, and join dates. |
| **Posts** | 5,000 | `data/posts.csv` | Categorized content posts with timestamps and engagement statistics. |
| **Comments** | 15,000 | `data/comments.csv` | Discussion threads with pre-labeled sentiment categories. |
| **Interactions** | 20,000 | `data/interactions.csv` | Granular event stream (views, likes, shares, comments). |

---

## Phase 3 — MongoDB

### Database Architecture
* **Database Name**: `social_media_analytics`
* **Driver**: PyMongo (`MongoClient`)
* **Connection Management**: Loaded securely via `.env` using `python-dotenv` with automatic fallback to `mongodb://localhost:27017/`.
* **Server Selection Timeout**: 5000ms to fail fast and report clear diagnostics if MongoDB is unreachable.

### Collections & Document Counts
* `users`: 1,000 documents
* `posts`: 5,000 documents
* `comments`: 15,000 documents
* `interactions`: 20,000 documents

### BSON Data Conversion
During ingestion from CSV to MongoDB, data types are transformed into native BSON types:
* **Timestamps / Dates**: Strings are parsed into native BSON `Date` (`ISODate`) objects (`join_date`, `timestamp`).
* **Numeric Fields**: Integers are preserved as native BSON integers (`age`, `followers`, `following`, `likes`, `shares`, `views`).
* **Hashtags**: Serialized hashtag strings are parsed into clean BSON arrays of strings (`["#Tech", "#Python", ...]`).
* **Primary / Reference Keys**: Preserved as clean business ID strings (`user_id`, `post_id`, `comment_id`, `interaction_id`).

### Indexing Strategy
To ensure optimal performance for MongoDB aggregation pipelines and analytical filtering, the following indexes are maintained:
* **`users`**: Unique index on `user_id`.
* **`posts`**: Unique index on `post_id`, plus ascending indexes on `user_id`, `category`, and `timestamp`.
* **`comments`**: Unique index on `comment_id`, plus ascending indexes on `post_id`, `user_id`, and `timestamp`.
* **`interactions`**: Unique index on `interaction_id`, plus ascending indexes on `user_id`, `post_id`, `interaction_type`, and `timestamp`.

### Safe Re-Running
The ingestion script `database/ingest_data.py` safely clears existing collection documents before ingestion, ensuring deterministic re-execution without duplicate key conflicts.

### Running Ingestion & Validation
```bash
# 1. Ingest dataset into MongoDB
python database/ingest_data.py

# 2. Validate database collections, types, references, and indexes
python database/validate_database.py
```

---

## Phase 4 — MongoDB Aggregation & Analytics

### Analyses Implemented

11 reusable analytical functions implemented in [`analytics/aggregation_queries.py`](analytics/aggregation_queries.py):

| # | Function | Description |
|---|---|---|
| 1 | `get_overview_metrics()` | Total users, posts, comments, interactions, views, likes, shares |
| 2 | `get_category_engagement()` | Engagement (likes + shares + comments) per post category |
| 3 | `get_top_posts(limit)` | Top N posts ranked by total engagement |
| 4 | `get_top_users(limit)` | Top N most active users by interaction count |
| 5 | `get_activity_over_time(granularity)` | Interactions per day or per month over the 12-month window |
| 6 | `get_interaction_type_distribution()` | Count of view / like / share / comment events |
| 7 | `get_top_hashtags(limit)` | Most-used hashtags via `$unwind` on the hashtags array |
| 8 | `get_sentiment_distribution()` | Positive / Neutral / Negative comment counts |
| 9 | `get_sentiment_by_category()` | Sentiment breakdown per post category |
| 10 | `get_location_engagement()` | Interactions and posts per Indian city |
| 11 | `get_peak_interaction_hours()` | Interaction counts by hour of day (0–23) |

### MongoDB Aggregation Operators Demonstrated

`$group` · `$sum` · `$sort` · `$project` · `$lookup` · `$unwind` · `$limit` · `$cond` · `$size` · `$add` · `$dateToString` · `$hour`

### Running the Analytics Tests

```bash
python analytics/test_analytics.py
```

Expected output:
```
Result: 12/12 analyses PASSED
```

### Analytics Documentation
- Full per-function documentation: [`analytics/ANALYTICS_DOCUMENTATION.md`](analytics/ANALYTICS_DOCUMENTATION.md)
- Quick-reference summary table: [`analytics/ANALYTICS_SUMMARY.md`](analytics/ANALYTICS_SUMMARY.md)

---

## Phase 5 — Streamlit Dashboard

### Dashboard Overview

The Streamlit dashboard provides an interactive visualization layer for the MongoDB analytics. It consists of five main pages accessible via a sidebar navigation:

| Page | Description |
|------|-------------|
| **Overview** | KPI cards, engagement by category, interaction type distribution, and top posts |
| **Content & Engagement** | Category engagement metrics, top hashtags, and most popular posts with adjustable limits |
| **Users & Locations** | Most active users, location analytics, and follower vs interaction comparison |
| **Sentiment Analysis** | Sentiment distribution, sentiment by category, and sentiment summary table |
| **Time & Activity** | Activity over time (daily/monthly) and peak interaction hours |

### Key Features

- **Interactive Plotly Charts**: Bar charts, pie/donut charts, line charts, and scatter plots
- **KPI Cards**: Real-time metrics for users, posts, comments, interactions, views, likes, and shares
- **Data Tables**: Clean tabular displays for top posts, top users, and sentiment summaries
- **Sidebar Navigation**: Easy switching between dashboard pages
- **Dataset Information**: Live counts from MongoDB displayed in the sidebar
- **Global Filters**: Category and sentiment filters (for future extension)
- **Data Caching**: Streamlit caching for responsive performance
- **Error Handling**: Clear error messages if MongoDB is unavailable
- **Explainability Section**: Documentation of MongoDB aggregation operations used

### Architecture

The dashboard follows a clean layered architecture:

```
Synthetic Dataset (CSV)
         ↓
    MongoDB
         ↓
Aggregation Functions (Phase 4)
         ↓
Streamlit + Plotly Dashboard
         ↓
Interactive Charts & Tables
```

**Important**: The dashboard does NOT duplicate MongoDB aggregation logic. It calls the existing functions from `analytics/aggregation_queries.py`, ensuring all calculations are performed in MongoDB.

### Visualizations Implemented

| Visualization | Type | Data Source |
|---------------|------|-------------|
| Engagement by Category | Bar Chart | `get_category_engagement()` |
| Interaction Type Distribution | Donut Chart | `get_interaction_type_distribution()` |
| Top Hashtags | Horizontal Bar Chart | `get_top_hashtags()` |
| Location Engagement | Bar Chart | `get_location_engagement()` |
| Sentiment Distribution | Donut Chart | `get_sentiment_distribution()` |
| Sentiment by Category | Stacked Bar Chart | `get_sentiment_by_category()` |
| Activity Over Time | Line Chart | `get_activity_over_time()` |
| Peak Interaction Hours | Bar Chart | `get_peak_interaction_hours()` |
| Followers vs Interactions | Scatter Plot | `get_top_users()` |
| Top Posts | Data Table | `get_top_posts()` |
| Top Users | Data Table | `get_top_users()` |

### Running the Dashboard

**Prerequisites:**
1. MongoDB must be running on `localhost:27017`
2. Dataset must be ingested into MongoDB (see Phase 3)
3. All dependencies installed (see `requirements.txt`)

**Start MongoDB:**
```bash
# Windows
mongod

# macOS/Linux
sudo systemctl start mongod
# or
mongod
```

**Run the Dashboard:**
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Dashboard Pages in Detail

**Overview Page:**
- 7 KPI cards showing total counts
- Engagement by category bar chart
- Interaction type distribution donut chart
- Top 10 posts table

**Content & Engagement Page:**
- Category engagement with metric selector (Total Engagement, Views, Likes, Shares, Number of Posts)
- Top 10 hashtags horizontal bar chart
- Most popular posts with slider (5-20 posts)

**Users & Locations Page:**
- Top 10 users table with detailed metrics
- Location engagement bar chart
- Followers vs interactions scatter plot

**Sentiment Analysis Page:**
- Sentiment distribution donut chart
- Sentiment by category stacked bar chart
- Sentiment summary table

**Time & Activity Page:**
- Activity over time line chart with daily/monthly granularity
- Peak interaction hours bar chart (0-23 hours)

---

## Planned Features

1. **Social-media data generation/import**: Creating or importing realistic social media data. *(Completed in Phase 2)*
2. **MongoDB storage & schema modeling**: Document ingestion, BSON conversions, and indexing. *(Completed in Phase 3)*
3. **MongoDB aggregation-based analytics**: 11 analytical functions using aggregation pipelines. *(Completed in Phase 4)*
4. **User/post/comment/interaction analysis**: Engagement, sentiment, hashtags, location, temporal trends. *(Completed in Phase 4)*
5. **Streamlit visualization dashboard**: Interactive charts and data filtering using Plotly and Streamlit. *(Completed in Phase 5)*

## Getting Started

1. Clone or navigate to the repository directory:
   ```bash
   cd social-media-analytics
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure `.env`:
   ```bash
   # Create .env from template
   cp .env.example .env
   # Ensure MONGODB_URI points to your running MongoDB instance
   ```

5. Generate the dataset:
   ```bash
   python data/generate_dataset.py
   ```

6. Ingest into MongoDB & validate:
   ```bash
   python database/ingest_data.py
   python database/validate_database.py
   ```

7. Run analytics tests:
   ```bash
   python analytics/test_analytics.py
   ```

8. Run the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

The dashboard will open at `http://localhost:8501` and provide interactive visualizations of all analytics.

---

### Filter Implementation

**Category Filter:**
- Applies to: Category engagement, Top posts, Top hashtags, Sentiment by category
- MongoDB operator: `$match` on `category` field
- Options: All, Technology, Sports, Entertainment, Travel, Education, Food, Fashion, Business, Health, Environment

**Sentiment Filter:**
- Applies to: Sentiment distribution, Sentiment by category
- MongoDB operator: `$match` on `sentiment` field with `$lookup` to posts for category filtering
- Options: All, Positive, Neutral, Negative

**Combined Filters:**
- Both filters can be applied simultaneously
- MongoDB processes filters server-side for optimal performance
- No client-side filtering of downloaded data

### Test Results

**Analytics Tests:** PASS (12/12 analyses)
- All 11 aggregation functions tested
- Backward compatibility verified
- Filter parameters validated

**Database Validation:** PASS
- All collections verified (1,000 users, 5,000 posts, 15,000 comments, 20,000 interactions)
- BSON datetime types confirmed
- Referential integrity validated
- Indexes verified

**Dashboard Logic Tests:** PASS (5/5 test groups)
- Backward compatibility: PASS
- Category filter: PASS
- Sentiment filter: PASS
- Combined filters: PASS
- Empty result handling: PASS

**Streamlit Startup:** PASS
- Application starts successfully
- MongoDB connection established
- All pages render correctly
- Filters function properly

### Final Dependencies

```
streamlit
pymongo
pandas
plotly
python-dotenv
```

No unnecessary dependencies. Core stack only.

### Security Check

✅ **No hardcoded credentials** - MongoDB configuration loaded from `.env` file
✅ **`.env` in `.gitignore`** - Environment variables excluded from version control
✅ **No API keys or secrets** - No external API integrations
✅ **Default localhost connection** - Safe for local development
✅ **Read-only dashboard** - No data modification operations

### Launch Command

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Notes

- This is an academic project for demonstration purposes
- All data is synthetic and generated for this project
- MongoDB should be running on `localhost:27017` before launching the dashboard
- The dashboard is designed for read-only analytics and data visualization
