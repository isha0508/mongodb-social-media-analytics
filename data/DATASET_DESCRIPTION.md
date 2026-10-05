# Dataset Description & Data Dictionary

This document provides a detailed data dictionary for the synthetic social-media datasets generated in **Phase 2** of the **MongoDB-Based Social Media Analytics** project.

---

## 1. Overview of Datasets

The project uses four relationally consistent datasets designed for NoSQL modeling and analytics:

| Dataset | File Path | Record Count | Description |
|---|---|---|---|
| **Users** | `data/users.csv` | 1,000 | User profile details, demographics, and social stats |
| **Posts** | `data/posts.csv` | 5,000 | Social media posts categorized by topic with engagement metrics |
| **Comments** | `data/comments.csv` | 15,000 | User comments on posts with labeled sentiments |
| **Interactions** | `data/interactions.csv` | 20,000 | Interaction events (views, likes, shares, comments) |

---

## 2. Data Dictionary

### 2.1 Users Dataset (`users.csv`)

| Field Name | Dataset | Data Type | Description | Example Value |
|---|---|---|---|---|
| `user_id` | Users | String | Unique primary identifier for each user | `USR_0001` |
| `username` | Users | String | Unique social media handle for the user | `nikhil_dev_35` |
| `age` | Users | Integer | Age of the user (18 to 65) | `31` |
| `gender` | Users | String | Gender identity (`Male`, `Female`, `Non-Binary`) | `Male` |
| `location` | Users | String | City of residence (one of 10 Indian cities) | `Bengaluru` |
| `followers` | Users | Integer | Number of users following this account | `705` |
| `following` | Users | Integer | Number of accounts followed by this user | `233` |
| `join_date` | Users | Date (`YYYY-MM-DD`) | Date the user registered their account | `2022-04-03` |

---

### 2.2 Posts Dataset (`posts.csv`)

| Field Name | Dataset | Data Type | Description | Example Value |
|---|---|---|---|---|
| `post_id` | Posts | String | Unique primary identifier for each post | `POST_0001` |
| `user_id` | Posts | String | Reference to author's `user_id` in `users.csv` | `USR_0372` |
| `content` | Posts | String | Text content of the social media post | `5 essential best practices for writing clean, modular Python in production. [Discussion #412]` |
| `category` | Posts | String | Topic category (one of 10 predefined categories) | `Technology` |
| `hashtags` | Posts | String | Category-specific hashtags associated with post | `#Tech #Python #Cloud` |
| `timestamp` | Posts | Datetime (`YYYY-MM-DD HH:MM:SS`) | Timestamp when the post was published | `2026-03-12 14:22:10` |
| `likes` | Posts | Integer | Number of likes received by the post | `842` |
| `shares` | Posts | Integer | Number of times the post was shared | `95` |
| `views` | Posts | Integer | Total number of post impressions/views | `6531` |

---

### 2.3 Comments Dataset (`comments.csv`)

| Field Name | Dataset | Data Type | Description | Example Value |
|---|---|---|---|---|
| `comment_id` | Comments | String | Unique primary identifier for each comment | `COM_00001` |
| `post_id` | Comments | String | Reference to the parent `post_id` in `posts.csv` | `POST_1856` |
| `user_id` | Comments | String | Reference to commenter's `user_id` in `users.csv` | `USR_0419` |
| `comment_text` | Comments | String | Text of the comment left on the post | `This is extremely insightful and well explained. Thanks for sharing!` |
| `timestamp` | Comments | Datetime (`YYYY-MM-DD HH:MM:SS`) | Timestamp when comment was made (>= post timestamp) | `2026-08-15 21:21:48` |
| `sentiment` | Comments | String | Labeled sentiment category (`Positive`, `Neutral`, `Negative`) | `Positive` |

---

### 2.4 Interactions Dataset (`interactions.csv`)

| Field Name | Dataset | Data Type | Description | Example Value |
|---|---|---|---|---|
| `interaction_id` | Interactions | String | Unique primary identifier for each interaction event | `INT_00001` |
| `user_id` | Interactions | String | Reference to user who performed the interaction | `USR_0655` |
| `post_id` | Interactions | String | Reference to target `post_id` in `posts.csv` | `POST_1865` |
| `interaction_type` | Interactions | String | Type of interaction (`view`, `like`, `share`, `comment`) | `view` |
| `timestamp` | Interactions | Datetime (`YYYY-MM-DD HH:MM:SS`) | Event timestamp (>= post timestamp) | `2025-11-18 23:38:09` |

---

## 3. Entity Relationships

```
  [ Users ]
  (user_id)
      │
      ├── (1:N) ──> [ Posts ] (post_id, user_id)
      │                 │
      ├── (1:N) ──┐     ├── (1:N) ──> [ Comments ] (comment_id, post_id, user_id)
      │           │     │
      └── (1:N) ──┴─────┴── (1:N) ──> [ Interactions ] (interaction_id, user_id, post_id)
```

* **Posts to Users**: Each post is authored by one valid `user_id`.
* **Comments to Posts & Users**: Each comment references an existing `post_id` and the commenting `user_id`.
* **Interactions to Posts & Users**: Each interaction logs an action performed by an existing `user_id` on an existing `post_id`.

---

## 4. Synthetic Data Disclaimer

All data in these files is synthetically generated for academic evaluation and big data analytics practice. No real individuals, proprietary entities, or real-world personal data are represented.
