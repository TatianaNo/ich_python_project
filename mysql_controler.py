import pymysql
from db_connector import close_all_connections, initialize_mysql
import logging

logger = logging.getLogger(__name__)

def get_head_row_from_mysql(query, params=None):
    """
    Execute a SQL query and return all rows and column headers.
    Args:
        query (str): SQL query to execute.
        params (tuple, optional): Parameters for the SQL query.
    Returns:
        tuple: (list of result dictionaries, list of column headers)
    """

    connection = initialize_mysql()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    results = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    return results, headers


def get_from_mysql(query, params=None) -> list:
    """
    Execute a SQL query and return results as a list of dictionaries.
    Args:
        query (str): SQL query to execute.
        params (tuple, optional): Parameters for the SQL query.
    Returns:
        list: List of result dictionaries.
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return []


def find_films_by_keyword(keyword, limit=10, skip=0):
    """
    Find films by keyword search in the MySQL database.
    Args:
        keyword (str): Keyword to search for.
        limit (int): Maximum number of results to return.
        skip (int): Number of results to skip (for pagination).
    Returns:
        tuple: (list of film dictionaries, list of column headers)
    """
    try:
        query = """
            SELECT ft.title, ft.description, f.release_year, c.name AS genre
            FROM film_text ft
            JOIN film f ON ft.film_id = f.film_id
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE LOWER(ft.title) LIKE %s
            LIMIT %s OFFSET %s;
        """
        search_pattern = f"%{keyword.lower()}%"
        params = (search_pattern, limit, skip)
        row, header = get_head_row_from_mysql(query, params)
        return row, header
    except Exception as e:
        logger.error(f"Error searching films by keyword '{keyword}': {e}")
        return []


def find_films_by_criteria(filter: dict, limit=10, skip=0):
    """
    Find films by genre and year criteria in the MySQL database.
    Args:
        filter (dict): Dictionary with filter keys (genre, year_from, year_to).
        limit (int): Maximum number of results to return.
        skip (int): Number of results to skip (for pagination).
    Returns:
        tuple: (list of film dictionaries, list of column headers)
    """
    try:
        text_filter = []
        param = []
        filter_res = ""
        for item, value in filter.items():
            if item == "genre":
                text_filter.append("c.name = %s")
            elif item == "year_from":
                text_filter.append("f.release_year >= %s")
            elif item == "year_to":
                text_filter.append("f.release_year <= %s")
            param.append(value)
        if text_filter:
            filter_res = "WHERE " + " and ".join(text_filter)
        param.append(limit)
        param.append(skip)
        query = f"""
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            {filter_res}
            LIMIT %s OFFSET %s
        """
        results, headers = get_head_row_from_mysql(query, tuple(param))
        return results, headers
    except Exception as e:
        logger.error(f"Error searching films by criteria: {e}")
        return []


def get_all_genres():
    """
    Get all unique genres from the MySQL films table.
    Returns:
        list: List of unique genre names (str).
    """
    try:
        query = """
        SELECT name AS genre
        FROM category
        """
        results = get_from_mysql(query)
        return [result["genre"] for result in results]
    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        return []


def count_films_by_genre(filtr):
    """
    Count total films by genre in the MySQL database.
    Args:
        filtr (dict): Dictionary with 'genre', 'year_from', and 'year_to'.
    Returns:
        int: Total number of films matching the criteria.
    """
    try:
        query = """
        SELECT COUNT(*) count_film
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s and f.release_year BETWEEN %s AND %s
        """
        params = (filtr["genre"], filtr["year_from"], filtr["year_to"])
        results = get_from_mysql(query, params)
        return results[0]["count_film"] if results else 0
    except Exception as e:
        logger.error(f"Error counting films by genre: {e}")
        return 0


def count_films_by_keyword(keyword):
    """
    Count total number of films matching a keyword in the MySQL database.
    Args:
        keyword (str): Keyword to search for.
    Returns:
        int: Total number of matching films.
    """
    try:
        sql = """
        SELECT COUNT(*) as total
        FROM film_text
        WHERE title LIKE %s
        """
        search_pattern = f"%{keyword}%"
        result = get_from_mysql(sql, (search_pattern,))
        return result[0]["total"] if result else 0
    except Exception as e:
        logger.error(f"Error counting films by keyword '{keyword}': {e}")
        return 0


def count_films_by_actor(actor_keyword):
    """
    Count total number of films matching an actor keyword in the MySQL database.
    Args:
        actor_keyword (str): Part of actor's name or surname.
    Returns:
        int: Total number of matching films.
    """
    try:
        like_keyword = f"%{actor_keyword.lower()}%"
        query = """
            SELECT COUNT(*) ct
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            WHERE LOWER(a.first_name) LIKE %s OR LOWER(a.last_name) LIKE %s
        """
        result = get_from_mysql(query, (like_keyword, like_keyword))
        return result[0]["ct"] if result else 0
    except Exception as e:
        logger.error(f"Error counting films by actor '{actor_keyword}': {e}")
        return 0


def find_films_by_actor_with_genre(actor_keyword, limit=10, skip=0):
    """
    Find films by part of actor's name or surname, with genre and year, with pagination.
    Args:
        actor_keyword (str): Part of actor's name or surname (case-insensitive).
        limit (int): Number of results per page.
        skip (int): Offset for pagination.
    Returns:
        tuple: (list of film dictionaries with actor, title, year, genre, list of column headers)
    """
    try:
        like_keyword = f"%{actor_keyword.lower()}%"
        query = """
            SELECT
                CONCAT(a.first_name, ' ', a.last_name) AS actor_name,
                f.title AS film_title,
                f.release_year,
                c.name AS genre
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE LOWER(a.first_name) LIKE %s OR LOWER(a.last_name) LIKE %s
            ORDER BY f.release_year
            LIMIT %s OFFSET %s
        """
        results, headers = get_head_row_from_mysql(
            query, (like_keyword, like_keyword, limit, skip)
        )
        return results, headers
    except Exception as e:
        logger.error(f"Error searching films by actor '{actor_keyword}': {e}")
        return []


def get_year_range():
    """
    Get the minimum and maximum year from the MySQL films table.
    Returns:
        dict or None: Dictionary with 'min_year' and 'max_year', or None if error.
    """
    try:
        sql = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM film
        """
        result = get_from_mysql(sql)
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting year range: {e}")
        return None


def close_mysql_connection():
    """
    Close all MySQL connections and clear the cache.
    """
    close_all_connections()
