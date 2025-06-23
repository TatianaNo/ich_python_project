import pymysql
from pymongo import MongoClient
from settings import settings
from datetime import datetime
import json
import os

# Global variables for connection caching
_mongo_client = None
_mongo_db = None
_mysql_connection = None
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

def initialize_mysql():
    """
    Initialize MySQL connection for films data with caching.
    """
    global _mysql_connection
    
    # Return cached connection if exists and is alive
    if _mysql_connection is not None:
        try:
            _mysql_connection.ping(reconnect=True)
            return _mysql_connection
        except Exception:
            _mysql_connection = None
    
    # Create new connection
    config = settings.get_mysql_config()
    _mysql_connection = pymysql.connect(**config)
    
    return _mysql_connection

def close_all_connections():
    """
    Close all database connections and clear cache.
    """
    global _mongo_client, _mongo_db, _mysql_connection
    
    # Close MongoDB connection
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
    
    # Close MySQL connection
    if _mysql_connection:
        _mysql_connection.close()
        _mysql_connection = None

# =====================================================
# MONGODB FUNCTIONS (Logs and Statistics)
# =====================================================

def log_search_query_to_file(query, search_type, results_count):
    """
    Log search query to local JSON file when MongoDB is not available.
    """
    try:
        log_file = 'search_logs.json'
        log_entry = {
            'query': query,
            'search_type': search_type,
            'timestamp': datetime.utcnow().isoformat(),
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
                'timestamp': datetime.utcnow(),
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

# =====================================================
# MYSQL FUNCTIONS (Films Data)
# =====================================================

def find_films_by_keyword(keyword, limit=10, skip=0):
    """
    Find films by keyword search in MySQL database.
    
    Args:
        keyword (str): Keyword to search for
        limit (int): Maximum number of results
        skip (int): Number of results to skip (for pagination)
    
    Returns:
        list: List of film dictionaries
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # найти первые 10 фильмов, где в названии встречается ключевое слово (например, 'Love')
        sql = """
        SELECT title, description
        FROM film_text
        WHERE title LIKE %s
        LIMIT %s OFFSET %s
        """
        
        search_pattern = f"%{keyword}%"
        cursor.execute(sql, (search_pattern, limit, skip))
        
        results = cursor.fetchall()
        cursor.close()
        
        # Log the search
        log_search_query(keyword, 'keyword', len(results))
        
        return results
        
    except Exception as e:
        print(f"Error searching films by keyword '{keyword}': {e}")
        return []

def find_films_by_criteria(genre=None, year_from=None, year_to=None, limit=10, skip=0):
    """
    Find films by genre and year criteria in MySQL database.
    
    Args:
        genre (str): Film genre to search for
        year_from (int): Minimum year
        year_to (int): Maximum year
        limit (int): Maximum number of results
        skip (int): Number of results to skip (for pagination)
    
    Returns:
        list: List of film dictionaries
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        if genre and year_from and year_to:
            # найти фильмы по жанру и диапазону годов
            sql = """
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (genre, year_from, year_to, limit, skip))
            
        elif genre:
            # найти первые 10 фильмов по жанру (например 'Comedy')
            sql = """
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (genre, limit, skip))
            
        elif year_from and year_to:
            # найти первые 10 фильмов по диапазону годов (например 2005-2012)
            sql = """
            SELECT title, release_year
            FROM film
            WHERE release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (year_from, year_to, limit, skip))
            
        else:
            # если никаких критериев не указано, возвращаем пустой результат
            return []
        
        results = cursor.fetchall()
        cursor.close()
        
        # Log the search
        search_criteria = f"genre:{genre}, years:{year_from}-{year_to}"
        log_search_query(search_criteria, 'genre_year', len(results))
        
        return results
        
    except Exception as e:
        print(f"Error searching films by criteria: {e}")
        return []

def get_all_genres():
    """
    Get all unique genres from MySQL films table.
    
    Returns:
        list: List of unique genres
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # вывести все категории
        sql = """
        SELECT name AS genre
        FROM category
        """
        cursor.execute(sql)
        
        results = cursor.fetchall()
        cursor.close()
        
        # Extract genre names from tuples
        genres = [row[0] for row in results]
        return genres
        
    except Exception as e:
        print(f"Error getting genres: {e}")
        return []

def get_year_range():
    """
    Get the minimum and maximum year from MySQL films table.
    
    Returns:
        dict: Dictionary with 'min_year' and 'max_year'
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # вывести мин и мах года выпуска фильма
        sql = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM film
        """
        cursor.execute(sql)
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'min_year': result[0],
                'max_year': result[1]
            }
        else:
            return {'min_year': None, 'max_year': None}
            
    except Exception as e:
        print(f"Error getting year range: {e}")
        return {'min_year': None, 'max_year': None}

# Legacy function for compatibility (can be removed later)
def find_film_by_key(key: str):
    """
    Find a film by key (ID or title) in MySQL database.
    
    Args:
        key (str): The key of the film to find.
    
    Returns:
        dict: The film document if found, otherwise None.
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Try to find by ID first, then by title
        sql = "SELECT * FROM films WHERE id = %s OR title = %s LIMIT 1"
        cursor.execute(sql, (key, key))
        
        result = cursor.fetchone()
        cursor.close()
        
        return result
        
    except Exception as e:
        print(f"Error finding film by key '{key}': {e}")
        return None

# Alias for backward compatibility
close_db_connection = close_all_connections

