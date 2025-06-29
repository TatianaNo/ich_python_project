# =====================================================
# MONGODB FUNCTIONS (Logs and Statistics)
# =====================================================

from datetime import datetime, timezone
import json
import os

from db import check_mongo_availability, initialize_mongo


def log_search_query(query, search_type, results_count):
    """
    Log search query to MongoDB or local file for statistics.
    
    Args:
        query (str): Search query text
        search_type (str): Type of search (keyword, genre_year)
        results_count (int): Number of results found
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db['search_queries']
            log_entry = {
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.now(timezone.utc),
                'results_count': results_count
            }
            
            logs_collection.insert_one(log_entry)
            return
            
        except Exception as e:
            print(f"Error logging to MongoDB: {e}")


def get_popular_queries(limit=5):
    """
    Get most popular search queries from MongoDB or local file.
    
    Args:
        limit (int): Maximum number of queries to return
    
    Returns:
        list: List of popular queries with counts
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db['search_queries']
            
            # Aggregate pipeline to count queries by text
            pipeline = [
                {
                    '$group': {
                        '_id': '$query',
                        'count': {'$sum': 1},
                        'search_type': {'$first': '$search_type'},
                        'last_searched': {'$max': '$timestamp'}
                    }
                },
                {
                    '$sort': {'count': -1}
                },
                {
                    '$limit': limit
                }
            ]
            
            results = list(logs_collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            print(f"Error getting popular queries from MongoDB: {e}")
