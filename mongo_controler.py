from datetime import datetime, timezone
import json
import os

from db_connector import check_mongo_availability, initialize_mongo, collection_name
import logging

logger = logging.getLogger(__name__)



def log_search_query(query, search_type, results_count):
    """
    Log a search query to MongoDB or a local file for statistics.

    Args:
        query (str): Search query text.
        search_type (str): Type of search (e.g., 'keyword', 'genre_year').
        results_count (int): Number of results found.

    Returns:
        None
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db[collection_name]
            log_entry = {
                "query": query,
                "search_type": search_type,
                "timestamp": datetime.now(timezone.utc),
                "results_count": results_count,
            }

            logs_collection.insert_one(log_entry)
            return

        except Exception as e:
            logger.error(f"Error logging to MongoDB: {e}")


def get_popular_queries(limit=5):
    """
    Get the most popular search queries from MongoDB or a local file.

    Args:
        limit (int): Maximum number of queries to return.

    Returns:
        list: List of popular queries with counts.
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db[collection_name]

            # Aggregate pipeline to count queries by text
            pipeline = [
                {
                    "$group": {
                        "_id": "$query",
                        "count": {"$sum": 1},
                        "search_type": {"$first": "$search_type"},
                        "last_searched": {"$max": "$timestamp"},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": limit},
            ]

            results = list(logs_collection.aggregate(pipeline))
            return results

        except Exception as e:
            logger.error(f"Error getting popular queries from MongoDB: {e}")


def get_last_queries(limit=10):
    """
    Get recent unique queries from MongoDB or a local file.

    Args:
        limit (int): Maximum number of queries to return.

    Returns:
        list: List of recent unique queries with counts.
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db[collection_name]

            # Aggregate pipeline to get recent unique queries
            pipeline = [
                {
                    "$group": {
                        "_id": "$query",
                        "count": {"$sum": 1},
                        "search_type": {"$first": "$search_type"},
                        "last_searched": {"$max": "$timestamp"},
                    }
                },
                {"$sort": {"last_searched": -1}},
                {"$limit": limit},
            ]

            results = list(logs_collection.aggregate(pipeline))
            return results

        except Exception as e:
            logger.error(f"Error getting recent queries from MongoDB: {e}")

    # Fallback to local file logging if MongoDB is not available
    log_file_path = "local_search_log.json"
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # Sort by timestamp and get the last `limit` entries
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs[:limit]

    return []
