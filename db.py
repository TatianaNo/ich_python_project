import pymysql
from pymongo import MongoClient
from settings import settings
from datetime import datetime
import json

# Global variables for connection caching
_mongo_client = None
_mongo_db = None
_mysql_connection = None

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

def log_search_query(query, search_type, results_count):
    """
    Log search query to MongoDB for statistics.
    
    Args:
        query (str): Search query text
        search_type (str): Type of search (keyword, genre_year)
        results_count (int): Number of results found
    """
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
        
    except Exception as e:
        print(f"Error logging search query: {e}")

def get_popular_queries(limit=5):
    """
    Get most popular search queries from MongoDB.
    
    Args:
        limit (int): Maximum number of queries to return
    
    Returns:
        list: List of popular queries with counts
    """
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
        print(f"Error getting popular queries: {e}")
        return []

def get_recent_queries(limit=5):
    """
    Get most recent search queries from MongoDB.
    
    Args:
        limit (int): Maximum number of queries to return
    
    Returns:
        list: List of recent queries
    """
    try:
        mongo_db = initialize_mongo()
        logs_collection = mongo_db['search_queries']
        
        results = list(logs_collection.find()
                      .sort('timestamp', -1)
                      .limit(limit))
        return results
        
    except Exception as e:
        print(f"Error getting recent queries: {e}")
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

