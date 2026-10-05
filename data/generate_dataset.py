"""
MongoDB-Based Social Media Analytics
Phase 2: Dataset Design and Generation

This script generates synthetic but realistic datasets for an academic Big Data project:
- Users (1,000 records)
- Posts (5,000 records)
- Comments (15,000 records)
- Interactions (20,000 records)

The generation is fully deterministic using fixed random seeds.
Relationships between users, posts, comments, and interactions are strictly preserved.
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Ensure UTF-8 output encoding for Windows command line compatibility
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Fixed random seed for reproducibility
RANDOM_SEED = 42

# Predefined categories as per requirements
CATEGORIES = [
    "Technology",
    "Sports",
    "Entertainment",
    "Travel",
    "Education",
    "Food",
    "Fashion",
    "Business",
    "Health",
    "Environment"
]

# Predefined locations (Indian cities)
LOCATIONS = [
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Pune",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Nashik"
]

# Base content templates per category
CATEGORY_CONTENT_TEMPLATES = {
    "Technology": [
        "Exploring the latest breakthroughs in open-source AI and LLM architectures.",
        "5 essential best practices for writing clean, modular Python in production.",
        "Why cloud cost optimization has become the top priority for engineering teams.",
        "Understanding NoSQL database design: when to choose document vs relational.",
        "The evolution of web frameworks: comparing performance and developer productivity."
    ],
    "Sports": [
        "What an incredible final over! The momentum shift in tonight's match was unreal.",
        "Morning training session completed. Building endurance for the upcoming city marathon.",
        "Tactical analysis of yesterday's football derby: high-pressing tactics executed perfectly.",
        "Consistent conditioning and adequate rest are the true secrets to peak athletic performance.",
        "A historic win for the national badminton squad on the international stage!"
    ],
    "Entertainment": [
        "Just watched the latest weekend theatrical release—cinematography was truly world-class.",
        "Live music festivals in the city always bring an unmatched crowd energy.",
        "Behind-the-scenes look at how independent film directors create magic with limited budgets.",
        "Revisiting classic cinema soundtracks that continue to define generations.",
        "Excited for the upcoming sci-fi series premiere streaming this Friday."
    ],
    "Travel": [
        "Witnessed a stunning sunrise over the ancient Aravali hills in Jaipur.",
        "Exploring hidden heritage cafes and artistic alleyways across North Kolkata.",
        "Monsoon road trip through the Western Ghats: lush green valleys and misty mountain roads.",
        "Tips for solo budget travel: packing light, finding local homestays, and exploring offbeat spots.",
        "The serene backwaters and sunset reflections offered an unforgettable weekend escape."
    ],
    "Education": [
        "A step-by-step roadmap for engineering students to master Data Structures and Algorithms.",
        "Why continuous self-directed learning is the most valuable skill in modern tech careers.",
        "Essential open-access resources and research papers for Big Data Analytics learners.",
        "Balancing college coursework, project deadlines, and internship interview preparation.",
        "How hands-on project building accelerates conceptual clarity far faster than passive reading."
    ],
    "Food": [
        "Sunday morning ritual: piping hot filter coffee paired with crispy artisanal dosas.",
        "Street food exploration trail: discovering the most authentic culinary gems in Old Delhi.",
        "A nutritious 15-minute Mediterranean salad bowl recipe perfect for busy weekdays.",
        "Baking sourdough from scratch: mastering hydration levels and sourdough fermentation.",
        "Exploring traditional regional spices and their rich cultural heritage in Indian cuisine."
    ],
    "Fashion": [
        "Minimalist and sustainable capsule wardrobe ideas for the upcoming festive season.",
        "How smart-casual tailoring redefined modern everyday workplace attire.",
        "Thrifting vintage jackets and styling them with contemporary everyday denim.",
        "Celebrating handloom textiles and the skilled artisans preserving traditional weaving techniques.",
        "Top color palette inspirations taking over street-style aesthetics this season."
    ],
    "Business": [
        "Key takeaways from our quarterly customer acquisition and user retention metrics.",
        "Bootstrapping vs raising venture capital: evaluating the strategic trade-offs for early founders.",
        "How modern direct-to-consumer brands are leveraging analytics to personalize buyer journeys.",
        "Understanding unit economics: why healthy gross margins matter more than top-line hype.",
        "The impact of digital payment infrastructure on micro-retail commerce growth."
    ],
    "Health": [
        "3 simple ergonomic posture adjustments to prevent chronic neck and back stiffness.",
        "The scientifically validated benefits of getting 7 to 8 hours of restorative sleep.",
        "Starting the morning with hydration, mindful stretching, and a 20-minute brisk walk.",
        "Debunking popular nutrition myths: why balanced whole foods always beat extreme fad diets.",
        "Mental wellness in high-stress work environments: setting boundaries and avoiding burnout."
    ],
    "Environment": [
        "Community tree plantation drive this weekend—join hands to expand our urban green cover!",
        "Rainwater harvesting in housing societies: practical, low-cost steps for water conservation.",
        "Ditching single-use plastics: three simple, sustainable swaps everyone can make today.",
        "Solar rooftop adoption is accelerating: clean energy independence is now more accessible than ever.",
        "Preserving local wetland ecosystems is vital for urban flood control and biodiversity."
    ]
}

CATEGORY_HASHTAGS = {
    "Technology": ["#Tech", "#ArtificialIntelligence", "#Python", "#DataEngineering", "#Cloud"],
    "Sports": ["#Sports", "#Cricket", "#Fitness", "#Football", "#MatchDay"],
    "Entertainment": ["#Cinema", "#Music", "#Entertainment", "#Movies", "#PopCulture"],
    "Travel": ["#Travel", "#Wanderlust", "#IncredibleIndia", "#Explore", "#TravelDiaries"],
    "Education": ["#Education", "#Learning", "#DataScience", "#Students", "#Coding"],
    "Food": ["#Foodie", "#IndianFood", "#StreetFood", "#HomeCooking", "#FoodLovers"],
    "Fashion": ["#Fashion", "#StyleInspo", "#OOTD", "#SustainableFashion", "#Trends"],
    "Business": ["#Business", "#Startup", "#Entrepreneurship", "#Economy", "#Growth"],
    "Health": ["#Health", "#Wellness", "#FitnessGoals", "#MentalHealth", "#HealthyLiving"],
    "Environment": ["#Environment", "#Sustainability", "#GoGreen", "#ClimateAction", "#Nature"]
}

# Comment templates with predefined sentiments
COMMENT_TEMPLATES = [
    # Positive
    ("This is extremely insightful and well explained. Thanks for sharing!", "Positive"),
    ("Absolutely love this perspective! Couldn't agree more.", "Positive"),
    ("Great quality post! Really helped me understand the topic better.", "Positive"),
    ("Fantastic work, keep sharing such high-value content!", "Positive"),
    ("Super helpful and practical. Bookmark-worthy material!", "Positive"),
    ("Brilliant analysis! Looking forward to your next update.", "Positive"),
    ("Inspiring read. Sharing this with my team immediately.", "Positive"),
    ("Totally on point! Kudos to you for putting this together.", "Positive"),

    # Neutral
    ("Could you please share the sources or reference links for this?", "Neutral"),
    ("Interesting take. Noting this down for future reference.", "Neutral"),
    ("Following this thread to see how others in the community view it.", "Neutral"),
    ("Where can I find more detailed documentation on this particular point?", "Neutral"),
    ("Makes sense in certain contexts, though results might vary across use-cases.", "Neutral"),
    ("Are there any case studies available demonstrating this in practice?", "Neutral"),
    ("Fair observation. Worth analyzing the nuances further.", "Neutral"),

    # Negative
    ("I respectfully disagree with this premise; reality is quite different.", "Negative"),
    ("Not very convinced by this argument. It overlooks several critical factors.", "Negative"),
    ("Looks quite overrated in my opinion, didn't find much practical value.", "Negative"),
    ("This approach did not work well when we attempted something similar.", "Negative"),
    ("A bit too generalized and lacks actionable depth.", "Negative"),
    ("The conclusions drawn here seem somewhat biased.", "Negative")
]


def generate_users(num_users=1000, seed=RANDOM_SEED):
    """Generates synthetic users dataset."""
    random.seed(seed)
    np.random.seed(seed)

    first_names = [
        "Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Sneha", "Ananya", "Rahul",
        "Kavita", "Arjun", "Pooja", "Amit", "Neha", "Varun", "Meera", "Karan",
        "Divya", "Siddharth", "Ishaan", "Tanvi", "Nikhil", "Riya", "Manish", "Swati"
    ]
    suffixes = [
        "tech", "dev", "travels", "foodie", "fit", "lens", "studio", "insights",
        "daily", "vibes", "explorer", "hub", "chronicles", "journal", "pulse"
    ]

    users = []
    # Base start date for user registration: 2021-01-01 to 2024-12-31
    base_start = datetime(2021, 1, 1)
    total_days = (datetime(2024, 12, 31) - base_start).days

    for i in range(1, num_users + 1):
        user_id = f"USR_{i:04d}"
        fname = random.choice(first_names)
        suf = random.choice(suffixes)
        num_suffix = random.randint(10, 999)
        username = f"{fname.lower()}_{suf}_{num_suffix}"

        # Age realistic distribution: 18 to 65, centered around young adults
        age = int(np.clip(np.random.normal(28, 8), 18, 65))

        # Gender: Realistic mix
        gender = random.choices(["Female", "Male", "Non-Binary"], weights=[0.48, 0.48, 0.04])[0]

        # Location
        location = random.choice(LOCATIONS)

        # Skewed follower distribution (Pareto-like: most have modest count, few have high count)
        # Power law / Pareto distribution
        follower_multiplier = float(np.random.pareto(a=2.2))
        followers = int(np.clip(50 + follower_multiplier * 800, 20, 50000))

        # Following: realistic bounds
        following = int(np.clip(np.random.normal(250, 120), 10, min(1500, followers * 3 + 50)))

        # Join date
        join_offset = random.randint(0, total_days)
        join_date = (base_start + timedelta(days=join_offset)).strftime("%Y-%m-%d")

        users.append({
            "user_id": user_id,
            "username": username,
            "age": age,
            "gender": gender,
            "location": location,
            "followers": followers,
            "following": following,
            "join_date": join_date
        })

    return pd.DataFrame(users)


def generate_posts(users_df, num_posts=5000, seed=RANDOM_SEED):
    """Generates synthetic posts dataset linked to existing users."""
    random.seed(seed)
    np.random.seed(seed)

    posts = []
    user_ids = users_df["user_id"].tolist()
    # Users with higher followers post slightly more frequently
    follower_weights = (users_df["followers"] ** 0.35).values
    follower_weights = follower_weights / follower_weights.sum()

    # Timeframe: Last 12 months (2025-10-01 00:00:00 to 2026-09-30 23:59:59)
    start_date = datetime(2025, 10, 1, 0, 0, 0)
    end_date = datetime(2026, 9, 30, 23, 59, 59)
    span_seconds = int((end_date - start_date).total_seconds())

    for i in range(1, num_posts + 1):
        post_id = f"POST_{i:04d}"
        user_id = np.random.choice(user_ids, p=follower_weights)
        category = random.choice(CATEGORIES)

        # Pick content template and add slight variation
        template = random.choice(CATEGORY_CONTENT_TEMPLATES[category])
        variation_suffix = f" [Discussion #{random.randint(101, 999)}]"
        content = f"{template}{variation_suffix}"

        # Hashtags
        tags_sample = random.sample(CATEGORY_HASHTAGS[category], k=random.randint(2, 4))
        hashtags = " ".join(tags_sample)

        # Distributed timestamp
        post_time = start_date + timedelta(seconds=random.randint(0, span_seconds))
        timestamp_str = post_time.strftime("%Y-%m-%d %H:%M:%S")

        # Category multiplier (some categories receive naturally higher engagement)
        category_multipliers = {
            "Technology": 1.25,
            "Entertainment": 1.30,
            "Sports": 1.20,
            "Food": 1.10,
            "Travel": 1.15,
            "Business": 1.05,
            "Fashion": 1.00,
            "Health": 0.95,
            "Education": 0.90,
            "Environment": 0.85
        }
        cat_mult = category_multipliers.get(category, 1.0)

        # Metric generation: views > likes > shares
        base_views = float(np.random.pareto(a=1.8)) * 1200 + random.randint(150, 800)
        views = int(np.clip(base_views * cat_mult, 100, 60000))

        # Likes: between 4% and 18% of views (at least 1, strictly < views)
        like_ratio = random.uniform(0.04, 0.18)
        likes = max(1, int(views * like_ratio))
        if likes >= views:
            likes = views - 1

        # Shares: between 2% and 14% of likes (strictly < likes)
        share_ratio = random.uniform(0.02, 0.14)
        shares = max(0, int(likes * share_ratio))
        if shares >= likes and likes > 0:
            shares = max(0, likes - 1)

        posts.append({
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "category": category,
            "hashtags": hashtags,
            "timestamp": timestamp_str,
            "likes": likes,
            "shares": shares,
            "views": views
        })

    return pd.DataFrame(posts)


def generate_comments(users_df, posts_df, num_comments=15000, seed=RANDOM_SEED):
    """Generates synthetic comments dataset linked to existing users and posts."""
    random.seed(seed)
    np.random.seed(seed)

    user_ids = users_df["user_id"].tolist()
    posts_list = posts_df[["post_id", "timestamp", "likes"]].to_dict("records")

    # Posts with higher likes naturally attract more comments
    likes_array = np.array([p["likes"] for p in posts_list], dtype=float)
    comment_weights = (likes_array + 10.0) ** 0.7
    comment_weights = comment_weights / comment_weights.sum()

    comments = []
    for i in range(1, num_comments + 1):
        comment_id = f"COM_{i:05d}"

        # Choose post based on engagement weights
        selected_post_idx = np.random.choice(len(posts_list), p=comment_weights)
        selected_post = posts_list[selected_post_idx]
        post_id = selected_post["post_id"]
        post_time = datetime.strptime(selected_post["timestamp"], "%Y-%m-%d %H:%M:%S")

        # Choose user
        user_id = random.choice(user_ids)

        # Comment text and deterministic sentiment assignment
        text_template, sentiment = random.choice(COMMENT_TEMPLATES)
        comment_text = text_template

        # Comment timestamp must be at or after post timestamp (within 1 to 72 hours)
        delay_minutes = random.randint(2, 4320)
        comment_time = post_time + timedelta(minutes=delay_minutes)
        timestamp_str = comment_time.strftime("%Y-%m-%d %H:%M:%S")

        comments.append({
            "comment_id": comment_id,
            "post_id": post_id,
            "user_id": user_id,
            "comment_text": comment_text,
            "timestamp": timestamp_str,
            "sentiment": sentiment
        })

    return pd.DataFrame(comments)


def generate_interactions(users_df, posts_df, num_interactions=20000, seed=RANDOM_SEED):
    """Generates synthetic interactions dataset linked to existing users and posts."""
    random.seed(seed)
    np.random.seed(seed)

    user_ids = users_df["user_id"].tolist()
    posts_list = posts_df[["post_id", "timestamp", "views"]].to_dict("records")

    # Posts with more views receive more interactions
    views_array = np.array([p["views"] for p in posts_list], dtype=float)
    interaction_weights = views_array ** 0.65
    interaction_weights = interaction_weights / interaction_weights.sum()

    # Interaction types with realistic distribution
    interaction_types = ["view", "like", "share", "comment"]
    interaction_type_weights = [0.55, 0.28, 0.07, 0.10]

    interactions = []
    for i in range(1, num_interactions + 1):
        interaction_id = f"INT_{i:05d}"

        selected_post_idx = np.random.choice(len(posts_list), p=interaction_weights)
        selected_post = posts_list[selected_post_idx]
        post_id = selected_post["post_id"]
        post_time = datetime.strptime(selected_post["timestamp"], "%Y-%m-%d %H:%M:%S")

        user_id = random.choice(user_ids)
        itype = random.choices(interaction_types, weights=interaction_type_weights)[0]

        # Interaction timestamp must be at or after post timestamp
        delay_minutes = random.randint(1, 2880)
        interaction_time = post_time + timedelta(minutes=delay_minutes)
        timestamp_str = interaction_time.strftime("%Y-%m-%d %H:%M:%S")

        interactions.append({
            "interaction_id": interaction_id,
            "user_id": user_id,
            "post_id": post_id,
            "interaction_type": itype,
            "timestamp": timestamp_str
        })

    return pd.DataFrame(interactions)


def validate_datasets(users_df, posts_df, comments_df, interactions_df):
    """
    Validates all dataset constraints and referential integrity.
    Returns True if all checks pass, otherwise raises AssertionError.
    """
    validations = []

    # 1. Record counts
    assert len(users_df) == 1000, f"Expected 1,000 users, got {len(users_df)}"
    assert len(posts_df) == 5000, f"Expected 5,000 posts, got {len(posts_df)}"
    assert len(comments_df) == 15000, f"Expected 15,000 comments, got {len(comments_df)}"
    assert len(interactions_df) == 20000, f"Expected 20,000 interactions, got {len(interactions_df)}"
    validations.append("Record counts correct (1,000 users, 5,000 posts, 15,000 comments, 20,000 interactions)")

    # 2. Unique primary IDs
    assert users_df["user_id"].is_unique, "Duplicate user_id detected!"
    assert posts_df["post_id"].is_unique, "Duplicate post_id detected!"
    assert comments_df["comment_id"].is_unique, "Duplicate comment_id detected!"
    assert interactions_df["interaction_id"].is_unique, "Duplicate interaction_id detected!"
    validations.append("IDs unique across all four datasets")

    # 3. Foreign key integrity
    user_id_set = set(users_df["user_id"])
    post_id_set = set(posts_df["post_id"])

    assert set(posts_df["user_id"]).issubset(user_id_set), "Unmatched user_id found in posts!"
    validations.append("Post user references valid")

    assert set(comments_df["post_id"]).issubset(post_id_set), "Unmatched post_id found in comments!"
    assert set(comments_df["user_id"]).issubset(user_id_set), "Unmatched user_id found in comments!"
    validations.append("Comment post and user references valid")

    assert set(interactions_df["post_id"]).issubset(post_id_set), "Unmatched post_id found in interactions!"
    assert set(interactions_df["user_id"]).issubset(user_id_set), "Unmatched user_id found in interactions!"
    validations.append("Interaction post and user references valid")

    # 4. No null or empty required fields
    for name, df in [("Users", users_df), ("Posts", posts_df), ("Comments", comments_df), ("Interactions", interactions_df)]:
        assert not df.isnull().values.any(), f"Null/missing values found in {name}!"
        for col in df.columns:
            if df[col].dtype == object:
                assert (df[col].str.strip() != "").all(), f"Empty string found in {name}.{col}!"
    validations.append("Required fields present with no null or empty values")

    # 5. Predefined categories and locations
    invalid_cats = set(posts_df["category"]) - set(CATEGORIES)
    assert len(invalid_cats) == 0, f"Invalid categories found: {invalid_cats}"
    validations.append("Categories valid (only predefined 10 categories)")

    invalid_locs = set(users_df["location"]) - set(LOCATIONS)
    assert len(invalid_locs) == 0, f"Invalid locations found: {invalid_locs}"
    validations.append("User locations valid (only predefined 10 cities)")

    # 6. Sentiment values
    allowed_sentiments = {"Positive", "Neutral", "Negative"}
    invalid_sents = set(comments_df["sentiment"]) - allowed_sentiments
    assert len(invalid_sents) == 0, f"Invalid sentiments found: {invalid_sents}"
    validations.append("Sentiments valid (Positive, Neutral, Negative)")

    # 7. Interaction types
    allowed_itypes = {"like", "share", "view", "comment"}
    invalid_itypes = set(interactions_df["interaction_type"]) - allowed_itypes
    assert len(invalid_itypes) == 0, f"Invalid interaction types found: {invalid_itypes}"
    validations.append("Interaction types valid (like, share, view, comment)")

    # 8. Numeric constraints
    assert (users_df["age"] >= 18).all() and (users_df["age"] <= 100).all(), "Invalid user age!"
    assert (users_df["followers"] >= 0).all() and (users_df["following"] >= 0).all(), "Negative user follower/following!"
    assert (posts_df["views"] >= posts_df["likes"]).all(), "Posts found where likes exceed views!"
    assert (posts_df["likes"] >= posts_df["shares"]).all(), "Posts found where shares exceed likes!"
    validations.append("Numeric relationships valid (views >= likes >= shares)")

    # 9. Chronological validity
    post_time_map = dict(zip(posts_df["post_id"], pd.to_datetime(posts_df["timestamp"])))

    comm_post_times = comments_df["post_id"].map(post_time_map)
    comm_times = pd.to_datetime(comments_df["timestamp"])
    assert (comm_times >= comm_post_times).all(), "Found comments timestamped before their parent post!"

    int_post_times = interactions_df["post_id"].map(post_time_map)
    int_times = pd.to_datetime(interactions_df["timestamp"])
    assert (int_times >= int_post_times).all(), "Found interactions timestamped before their parent post!"
    # Assertions have all passed
    return [
        "IDs unique",
        "User references valid",
        "Post references valid",
        "Comment references valid",
        "Interaction references valid",
        "Required fields present",
        "Categories valid",
        "Sentiments valid"
    ]


def main():
    print("=" * 60)
    print("MongoDB-Based Social Media Analytics - Phase 2 Dataset Generator")
    print("=" * 60)

    # Resolve output directory to 'data/' folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir if os.path.basename(script_dir) == "data" else os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("\n[1/4] Generating Users dataset (1,000 records)...")
    users_df = generate_users(num_users=1000)

    print("[2/4] Generating Posts dataset (5,000 records)...")
    posts_df = generate_posts(users_df, num_posts=5000)

    print("[3/4] Generating Comments dataset (15,000 records)...")
    comments_df = generate_comments(users_df, posts_df, num_comments=15000)

    print("[4/4] Generating Interactions dataset (20,000 records)...")
    interactions_df = generate_interactions(users_df, posts_df, num_interactions=20000)

    # Run validation
    print("\nRunning validation checks...")
    validation_results = validate_datasets(users_df, posts_df, comments_df, interactions_df)

    # Save to CSV
    users_csv = os.path.join(data_dir, "users.csv")
    posts_csv = os.path.join(data_dir, "posts.csv")
    comments_csv = os.path.join(data_dir, "comments.csv")
    interactions_csv = os.path.join(data_dir, "interactions.csv")

    users_df.to_csv(users_csv, index=False)
    posts_df.to_csv(posts_csv, index=False)
    comments_df.to_csv(comments_csv, index=False)
    interactions_df.to_csv(interactions_csv, index=False)

    print("\nDataset generation complete.\n")
    print(f"Users: {len(users_df):,}")
    print(f"Posts: {len(posts_df):,}")
    print(f"Comments: {len(comments_df):,}")
    print(f"Interactions: {len(interactions_df):,}")

    # Determine safe symbol for checkmark
    check_sym = "✓"
    try:
        check_sym.encode(sys.stdout.encoding or "utf-8")
    except Exception:
        check_sym = "[PASS]"

    print("\nValidation:")
    for result in validation_results:
        print(f"{check_sym} {result}")

    print(f"\nFiles successfully saved to: {data_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
