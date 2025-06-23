# Log writer for MongoDB and file-based logging
from pymongo import MongoClient
from settings import settings
from datetime import datetime, timezone
import json
import os

# Global variables for connection caching
_mongo_client = None
_mongo_db = None
_mongo_available = None

def check_mongo_availability():
    """
    Check if MongoDB is available and working.
    """
    global _mongo_available
    if _mongo_available is not None:
        return _mongo_available
    
    try:
        mongo_config = settings.get_mongo_config()
        client = MongoClient(mongo_config['uri'], serverSelectionTimeoutMS=3000)
        # Try to ping the server
        client.admin.command('ping')
        _mongo_available = True
        return True
    except Exception as e:
        _mongo_available = False
        print(f"⚠ MongoDB недоступен: {e}")
        print("   Логирование будет производиться в локальный файл")
        return False

def initialize_mongo():
    """
    Initialize MongoDB connection for logs and statistics with caching.
    """
    global _mongo_client, _mongo_db
    
    # Return cached connection if exists
    if _mongo_client is not None and _mongo_db is not None:
        try:
            # Test connection to make sure it's still alive
            _mongo_client.admin.command('ping')
            return _mongo_db
        except Exception:
            # Connection is dead, reset cache
            _mongo_client = None
            _mongo_db = None
    
    # Create new connection
    connection_string = settings.get_mongo_connection_string()
    _mongo_client = MongoClient(connection_string)
    _mongo_db = _mongo_client[settings.MONGO_DB_NAME]
    
    return _mongo_db

def close_mongo_connection():
    """
    Close MongoDB connection and clear cache.
    """
    global _mongo_client, _mongo_db
    
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None

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
