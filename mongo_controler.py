# =====================================================
# MONGODB FUNCTIONS (Logs and Statistics)
# =====================================================

from datetime import datetime, timezone
import json
import os

from db import check_mongo_availability, initialize_mongo

def log_search_query_to_file(query, search_type, results_count):
    """
    Log search query to local JSON file when MongoDB is not available.
    """
    try:
        log_file = 'search_logs.json'
        log_entry = {
            'query': query,
            'search_type': search_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results_count': results_count
        }
        
        # Read existing logs
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Ошибка при записи в файл логов: {e}")

def get_popular_queries_from_file(limit=5):
    """
    Get most popular search queries from local file.
    """
    try:
        log_file = 'search_logs.json'
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # Count query frequency
        query_counts = {}
        for log in logs:
            query = log.get('query', '').lower().strip()
            if query:
                query_counts[query] = query_counts.get(query, 0) + 1
        
        # Sort by frequency and return top queries
        popular_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'query': q, 'count': c} for q, c in popular_queries[:limit]]
        
    except Exception as e:
        print(f"Ошибка при чтении файла логов: {e}")
        return []

def get_search_stats_from_file():
    """
    Get search statistics from local file.
    """
    try:
        log_file = 'search_logs.json'
        if not os.path.exists(log_file):
            return {'total_searches': 0, 'search_types': {}}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        total_searches = len(logs)
        search_types = {}
        
        for log in logs:
            search_type = log.get('search_type', 'unknown')
            search_types[search_type] = search_types.get(search_type, 0) + 1
        
        return {
            'total_searches': total_searches,
            'search_types': search_types
        }
        
    except Exception as e:
        print(f"Ошибка при получении статистики из файла: {e}")
        return {'total_searches': 0, 'search_types': {}}

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
            print("Переключение на файловое логирование...")
    
    # Fallback to file logging
    log_search_query_to_file(query, search_type, results_count)

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
            print("Переключение на файловое получение статистики...")
    
    # Fallback to file-based queries
    return get_popular_queries_from_file(limit)

def get_recent_queries(limit=5):
    """
    Get most recent search queries from MongoDB or local file.
    
    Args:
        limit (int): Maximum number of queries to return
    
    Returns:
        list: List of recent queries
    """
    # Try MongoDB first if available
    if check_mongo_availability():
        try:
            mongo_db = initialize_mongo()
            logs_collection = mongo_db['search_queries']
            
            results = list(logs_collection.find()
                          .sort('timestamp', -1)
                          .limit(limit))
            return results
            
        except Exception as e:
            print(f"Error getting recent queries from MongoDB: {e}")
            print("Переключение на файловое получение данных...")
    
    # Fallback to file-based queries (get recent from file)
    try:
        log_file = 'search_logs.json'
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # Sort by timestamp and return most recent
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
        return sorted_logs[:limit]
        
    except Exception as e:
        print(f"Error getting recent queries from file: {e}")
        return []
