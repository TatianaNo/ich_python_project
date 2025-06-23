# MySQL connection and film search functions
import pymysql
from settings import settings

# Global variable for connection caching
_mysql_connection = None

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

def close_mysql_connection():
    """
    Close MySQL connection and clear cache.
    """
    global _mysql_connection
    
    if _mysql_connection:
        _mysql_connection.close()
        _mysql_connection = None

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
        
        return results
        
    except Exception as e:
        print(f"Error searching films by keyword '{keyword}': {e}")
        return []

def count_films_by_keyword(keyword):
    """
    Count total number of films matching keyword.
    
    Args:
        keyword (str): Keyword to search for
    
    Returns:
        int: Total number of matching films
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        sql = """
        SELECT COUNT(*) as total
        FROM film_text
        WHERE title LIKE %s
        """
        
        search_pattern = f"%{keyword}%"
        cursor.execute(sql, (search_pattern,))
        
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error counting films by keyword '{keyword}': {e}")
        return 0

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
        
        return results
        
    except Exception as e:
        print(f"Error searching films by criteria: {e}")
        return []

def get_all_genres():
    """
    Get all available genres from MySQL database.
    
    Returns:
        list: List of genre names
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        sql = "SELECT name AS genre FROM category"
        cursor.execute(sql)
        
        results = cursor.fetchall()
        cursor.close()
        
        return [result[0] for result in results]
        
    except Exception as e:
        print(f"Error getting genres: {e}")
        return []

def find_films_by_genre(genre, limit=10, skip=0):
    """
    Find films by genre in MySQL database.
    
    Args:
        genre (str): Genre to search for
        limit (int): Maximum number of results
        skip (int): Number of results to skip (for pagination)
    
    Returns:
        list: List of film dictionaries
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        sql = """
        SELECT f.title, f.release_year, c.name AS genre
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(sql, (genre, limit, skip))
        results = cursor.fetchall()
        cursor.close()
        
        films = []
        for result in results:
            films.append({
                'title': result[0],
                'release_year': result[1],
                'genre': result[2]
            })
        
        return films
        
    except Exception as e:
        print(f"Error finding films by genre: {e}")
        return []

def count_films_by_genre(genre):
    """
    Count total films by genre in MySQL database.
    
    Args:
        genre (str): Genre to count films for
    
    Returns:
        int: Total number of films
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        sql = """
        SELECT COUNT(*) 
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s
        """
        
        cursor.execute(sql, (genre,))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error counting films by genre: {e}")
        return 0

def find_films_by_year_range(year_from=None, year_to=None, limit=10, skip=0):
    """
    Find films by year range in MySQL database.
    
    Args:
        year_from (int): Start year (inclusive)
        year_to (int): End year (inclusive)
        limit (int): Maximum number of results
        skip (int): Number of results to skip (for pagination)
    
    Returns:
        list: List of film dictionaries
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # Build SQL query based on provided parameters
        if year_from and year_to:
            sql = """
            SELECT title, release_year
            FROM film
            WHERE release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (year_from, year_to, limit, skip))
        elif year_from:
            sql = """
            SELECT title, release_year
            FROM film
            WHERE release_year >= %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (year_from, limit, skip))
        elif year_to:
            sql = """
            SELECT title, release_year
            FROM film
            WHERE release_year <= %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (year_to, limit, skip))
        else:
            sql = """
            SELECT title, release_year
            FROM film
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (limit, skip))
        
        results = cursor.fetchall()
        cursor.close()
        
        films = []
        for result in results:
            films.append({
                'title': result[0],
                'release_year': result[1]
            })
        
        return films
        
    except Exception as e:
        print(f"Error finding films by year range: {e}")
        return []

def count_films_by_year_range(year_from=None, year_to=None):
    """
    Count total films by year range in MySQL database.
    
    Args:
        year_from (int): Start year (inclusive)
        year_to (int): End year (inclusive)
    
    Returns:
        int: Total number of films
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # Build SQL query based on provided parameters
        if year_from and year_to:
            sql = """
            SELECT COUNT(*) 
            FROM film
            WHERE release_year BETWEEN %s AND %s
            """
            cursor.execute(sql, (year_from, year_to))
        elif year_from:
            sql = """
            SELECT COUNT(*) 
            FROM film
            WHERE release_year >= %s
            """
            cursor.execute(sql, (year_from,))
        elif year_to:
            sql = """
            SELECT COUNT(*) 
            FROM film
            WHERE release_year <= %s
            """
            cursor.execute(sql, (year_to,))
        else:
            sql = "SELECT COUNT(*) FROM film"
            cursor.execute(sql)
        
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error counting films by year range: {e}")
        return 0

# Update get_year_range function to return tuple instead of dict
def get_year_range():
    """
    Get the minimum and maximum year from MySQL films table.
    
    Returns:
        tuple: (min_year, max_year) or None if error
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        sql = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM film
        """
        cursor.execute(sql)
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return (result[0], result[1])
        else:
            return None
            
    except Exception as e:
        print(f"Error getting year range: {e}")
        return None
