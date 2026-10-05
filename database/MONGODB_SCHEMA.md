# MongoDB Schema Documentation

This document describes the schema design, data types, indexes, and document structures for the **social_media_analytics** database in MongoDB.

---

## 1. Overview & Architecture

* **Database Name**: `social_media_analytics`
* **Driver**: PyMongo (`>=4.0`)
* **Data Format**: BSON (Binary JSON)
* **Number of Collections**: 4 (`users`, `posts`, `comments`, `interactions`)
* **Inspection Tool**: Standard MongoDB Compass or mongosh

### Why MongoDB is Suitable for this Project
1. **Document-Oriented Storage**: Social media entities naturally map to JSON-like documents (e.g., nested hashtags as arrays, timestamps as BSON dates).
2. **Schema Flexibility & Evolution**: In later phases, embedded subdocuments or additional analytics metadata can be attached without costly table migrations.
3. **Powerful Aggregation Framework**: MongoDB's pipeline stages (`$match`, `$group`, `$project`, `$sort`, `$unwind`, `$lookup`) provide high-performance in-database analytical compute capabilities without requiring heavy ETL jobs.
4. **Rich Indexing**: Secondary and unique BSON indexes ensure fast querying across foreign-key-like attributes (`user_id`, `post_id`) and temporal fields (`timestamp`).

---

## 2. Conceptual Structure & Entity Relationships

```
users
│
├── user_id (PK, Unique)
├── username
├── age
├── gender
├── location
├── followers
├── following
└── join_date (BSON Date)
│
▼
posts
│
├── post_id (PK, Unique)
├── user_id (Ref -> users.user_id)
├── content
├── category
├── hashtags (Array of Strings)
├── timestamp (BSON Date)
├── likes
├── shares
└── views
│
├──────────────────────────────► comments
│                                │
│                                ├── comment_id (PK, Unique)
│                                ├── post_id (Ref -> posts.post_id)
│                                ├── user_id (Ref -> users.user_id)
│                                ├── comment_text
│                                ├── timestamp (BSON Date)
│                                └── sentiment (Positive | Neutral | Negative)
│
└──────────────────────────────► interactions
                                 │
                                 ├── interaction_id (PK, Unique)
                                 ├── user_id (Ref -> users.user_id)
                                 ├── post_id (Ref -> posts.post_id)
                                 ├── interaction_type (view | like | share | comment)
                                 └── timestamp (BSON Date)
```

---

## 3. Collections & Document Schemas

### 3.1 `users` Collection (1,000 documents)

Represents registered platform users and demographic information.

| Field | BSON Type | Description | Index |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key | Standard |
| `user_id` | `String` | Business primary key (e.g. `"USR_0001"`) | **Unique Index** |
| `username` | `String` | User social handle (e.g. `"nikhil_dev_35"`) | None |
| `age` | `Int32` | User age (18 to 65) | None |
| `gender` | `String` | Gender identity (`"Male"`, `"Female"`, `"Non-Binary"`) | None |
| `location` | `String` | Indian city location (e.g. `"Bengaluru"`) | None |
| `followers` | `Int32` | Follower count | None |
| `following` | `Int32` | Following count | None |
| `join_date` | `Date` | Registration timestamp (`ISODate`) | None |

**Sample Document in MongoDB Compass:**
```json
{
  "_id": { "$oid": "660dc..." },
  "user_id": "USR_0001",
  "username": "nikhil_dev_35",
  "age": 31,
  "gender": "Male",
  "location": "Bengaluru",
  "followers": 705,
  "following": 233,
  "join_date": { "$date": "2022-04-03T00:00:00.000Z" }
}
```

---

### 3.2 `posts` Collection (5,000 documents)

Represents user content posts with engagement metrics and categorized topics.

| Field | BSON Type | Description | Index |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key | Standard |
| `post_id` | `String` | Business primary key (e.g. `"POST_0001"`) | **Unique Index** |
| `user_id` | `String` | Reference to author `users.user_id` | **Ascending Index** |
| `content` | `String` | Post body text | None |
| `category` | `String` | Content category (e.g. `"Technology"`) | **Ascending Index** |
| `hashtags` | `Array[String]` | Array of tags (e.g. `["#Tech", "#Python"]`) | None |
| `timestamp` | `Date` | Publication timestamp (`ISODate`) | **Ascending Index** |
| `likes` | `Int32` | Likes counter | None |
| `shares` | `Int32` | Shares counter | None |
| `views` | `Int32` | Total view impressions counter | None |

**Sample Document in MongoDB Compass:**
```json
{
  "_id": { "$oid": "660dc..." },
  "post_id": "POST_0001",
  "user_id": "USR_0372",
  "content": "Exploring the latest breakthroughs in open-source AI and LLM architectures. [Discussion #824]",
  "category": "Technology",
  "hashtags": ["#Tech", "#Python", "#Cloud"],
  "timestamp": { "$date": "2026-03-12T14:22:10.000Z" },
  "likes": 842,
  "shares": 95,
  "views": 6531
}
```

---

### 3.3 `comments` Collection (15,000 documents)

Represents user comments made on posts, labeled with sentiment values.

| Field | BSON Type | Description | Index |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key | Standard |
| `comment_id` | `String` | Business primary key (e.g. `"COM_00001"`) | **Unique Index** |
| `post_id` | `String` | Reference to parent `posts.post_id` | **Ascending Index** |
| `user_id` | `String` | Reference to commenter `users.user_id` | **Ascending Index** |
| `comment_text`| `String` | Text content of the comment | None |
| `timestamp` | `Date` | Timestamp of comment creation (`ISODate`) | **Ascending Index** |
| `sentiment` | `String` | Labeled sentiment (`"Positive"`, `"Neutral"`, `"Negative"`) | None |

**Sample Document in MongoDB Compass:**
```json
{
  "_id": { "$oid": "660dc..." },
  "comment_id": "COM_00001",
  "post_id": "POST_1856",
  "user_id": "USR_0419",
  "comment_text": "This is extremely insightful and well explained. Thanks for sharing!",
  "timestamp": { "$date": "2026-08-15T21:21:48.000Z" },
  "sentiment": "Positive"
}
```

---

### 3.4 `interactions` Collection (20,000 documents)

Represents event streams of user interactions across posts.

| Field | BSON Type | Description | Index |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key | Standard |
| `interaction_id`| `String` | Business primary key (e.g. `"INT_00001"`) | **Unique Index** |
| `user_id` | `String` | Reference to interacting user `users.user_id` | **Ascending Index** |
| `post_id` | `String` | Reference to target `posts.post_id` | **Ascending Index** |
| `interaction_type`| `String` | Type of action (`"view"`, `"like"`, `"share"`, `"comment"`)| **Ascending Index** |
| `timestamp` | `Date` | Timestamp of interaction (`ISODate`) | **Ascending Index** |

**Sample Document in MongoDB Compass:**
```json
{
  "_id": { "$oid": "660dc..." },
  "interaction_id": "INT_00001",
  "user_id": "USR_0655",
  "post_id": "POST_1865",
  "interaction_type": "view",
  "timestamp": { "$date": "2025-11-18T23:38:09.000Z" }
}
```

---

## 4. Index Inventory

All indexes are verified to optimize querying and pipeline execution:

| Collection | Index Name | Key(s) | Properties |
|---|---|---|---|
| `users` | `idx_user_id_unique` | `user_id: 1` | `unique: true` |
| `posts` | `idx_post_id_unique` | `post_id: 1` | `unique: true` |
| `posts` | `idx_posts_user_id` | `user_id: 1` | Standard |
| `posts` | `idx_posts_category` | `category: 1` | Standard |
| `posts` | `idx_posts_timestamp` | `timestamp: 1` | Standard |
| `comments` | `idx_comment_id_unique` | `comment_id: 1` | `unique: true` |
| `comments` | `idx_comments_post_id` | `post_id: 1` | Standard |
| `comments` | `idx_comments_user_id` | `user_id: 1` | Standard |
| `comments` | `idx_comments_timestamp` | `timestamp: 1` | Standard |
| `interactions` | `idx_interaction_id_unique` | `interaction_id: 1` | `unique: true` |
| `interactions` | `idx_interactions_user_id` | `user_id: 1` | Standard |
| `interactions` | `idx_interactions_post_id` | `post_id: 1` | Standard |
| `interactions` | `idx_interactions_type` | `interaction_type: 1` | Standard |
| `interactions` | `idx_interactions_timestamp` | `timestamp: 1` | Standard |

---

## 5. MongoDB Compass Verification Guide

To inspect the database in MongoDB Compass:
1. Open **MongoDB Compass**.
2. Connect using the connection string: `mongodb://localhost:27017`
3. In the left database pane, click `social_media_analytics`.
4. Inspect the four collections:
   * **Documents view**: Verify that dates render with the `ISODate` badge and `hashtags` render as array pills.
   * **Schema tab**: Run schema analysis to view field distributions and data types.
   * **Indexes tab**: Verify the registered single and unique indexes.
