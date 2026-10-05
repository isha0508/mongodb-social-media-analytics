"""
MongoDB Database Connection Module
Phase 3: Schema Modeling and Data Ingestion

Provides a clean, reusable database connection using PyMongo and python-dotenv.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env file in project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=dotenv_path)

DEFAULT_URI = "mongodb://localhost:27017/"
DEFAULT_DATABASE = "social_media_analytics"


def get_connection_config():
    """Retrieves MongoDB URI and database name from environment variables."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DATABASE")

    if not mongo_uri or not mongo_uri.strip():
        mongo_uri = DEFAULT_URI
    if not db_name or not db_name.strip():
        db_name = DEFAULT_DATABASE

    return mongo_uri.strip(), db_name.strip()


def get_database(server_timeout_ms=5000):
    """
    Establishes connection to MongoDB and returns the database object.

    Parameters:
        server_timeout_ms (int): Timeout in milliseconds for server selection.

    Returns:
        tuple: (db, client) where db is the Database object and client is the MongoClient.

    Raises:
        ConnectionFailure: When unable to connect or ping the MongoDB server.
    """
    mongo_uri, db_name = get_connection_config()

    try:
        # Initialize client with timeout to prevent hanging indefinitely
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=server_timeout_ms)

        # Validate connection via ping
        client.admin.command("ping")

        db = client[db_name]
        return db, client
    except (ConnectionFailure, ServerSelectionTimeoutError) as err:
        print(f"[ERROR] Could not connect to MongoDB at '{mongo_uri}': {err}")
        raise


if __name__ == "__main__":
    print("Testing MongoDB connection...")
    try:
        db, client = get_database()
        print(f"MongoDB connection SUCCESSFUL. Connected to database: '{db.name}'")
        client.close()
    except Exception as e:
        print(f"MongoDB connection FAILED: {e}")
