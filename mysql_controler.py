# =====================================================
# MYSQL FUNCTIONS (Films Data)
# =====================================================

import pandas as pd
import pymysql
from db import close_all_connections, initialize_mysql, initialize_mysql_engine
from mongo_controler import log_search_query

# Установка отображения всех строк и столбцов
pd.set_option('display.max_rows', None)     # Показывать все строки
pd.set_option('display.max_columns', None)  # Показывать все столбцы
pd.set_option('display.width', 0)           # Автоматическая ширина
pd.set_option('display.max_colwidth', None) # Показывать весь текст в ячейках



def get_head_row_from_mysql(query, params=None):
    """ Execute a SQL query and return the first row and headers.
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the SQL query
    Returns:
        tuple: (first row as a list of dictionaries, headers as a list)
    """

    connection = initialize_mysql()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    results = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    return results, headers 

def get_from_mysql(query, params=None) -> list:
    """
    Execute a SQL query and return results as a list.
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the SQL query
        Returns:
        list: List of results
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()    


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
        query = '''
            SELECT ft.title, ft.description, f.release_year, c.name AS genre
            FROM film_text ft
            JOIN film f ON ft.film_id = f.film_id
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE LOWER(ft.title) LIKE %s
            LIMIT %s OFFSET %s;
        '''
        search_pattern = f"%{keyword.lower()}%"
        


        
        params=(search_pattern, limit, skip)

        row, header = get_head_row_from_mysql(query, params)
        # Log the search
        log_search_query(keyword, 'keyword', len(row))
        
        return row, header
        
    except Exception as e:
        print(f"Error searching films by keyword '{keyword}': {e}")
        return []

def find_films_by_criteria(filter :dict, limit=10, skip=0):
    """
    Find films by genre and year criteria in MySQL database.
    
    Args:
        filtr (dict): 
    Returns:
        list: List of film dictionaries
    """
    try:
        text_filter = []
        param = []
        filter_res = ""
        genre = ""
        year_from =""
        year_to = ""

        for item, value in filter.items():
            if item == 'genre':
                text_filter.append('c.name = %s')
                genre = value 
            elif item == 'year_from':
                text_filter.append('f.release_year >= %s')
                year_from = value
            elif item == 'year_to':
                text_filter.append('f.release_year <= %s')
                year_to = value
            param.append(value)
        if text_filter:
            filter_res = "WHERE "+  ' and '.join(text_filter)
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
        
        search_criteria = f"genre:{genre}, years:{year_from}-{year_to}"
        
        results, headers = get_head_row_from_mysql(query, tuple(param))
        log_search_query(search_criteria, 'genre_year', len(results))

        return results, headers
        
    except Exception as e:
        print(f"Error searching films by criteria: {e}")
        return []

def get_all_genres() -> pd.DataFrame:
    """
    Get all unique genres from MySQL films table.
    
    Returns:
        list: List of unique genres
    """
    try:
        # вывести все категории
        query = """
        SELECT name AS genre
        FROM category
        """
        
        results = get_from_mysql(query)
        return [result["genre"] for result in results]
        
    except Exception as e:
        print(f"Error getting genres: {e}")
        return []



def count_films_by_genre(filtr):
    """
    Count total films by genre in MySQL database.
    
    Args:
        filtr (dict): Genre to count films for
    
    Returns:
        int: Total number of films
    """
    try:
        
        query = """
        SELECT COUNT(*) count_film
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s and f.release_year BETWEEN %s AND %s
        """
        
        params = (filtr['genre'],filtr['year_from'], filtr['year_to'])
        results = get_from_mysql(query, params)
        
        return results[0]['count_film'] if results else 0
        
    except Exception as e:
        print(f"Error counting films by genre: {e}")
        return 0
    

# =====================================================
# Additional functions for MySQL no pandas
# =====================================================    

def count_films_by_keyword(keyword):
    """
    Count total number of films matching keyword.
    
    Args:
        keyword (str): Keyword to search for
    
    Returns:
        int: Total number of matching films
    """
    try:
        sql = """
        SELECT COUNT(*) as total
        FROM film_text
        WHERE title LIKE %s
        """
        search_pattern = f"%{keyword}%"
        
        result =  get_from_mysql(sql, (search_pattern,))
        
        return result[0]['total'] if result else 0
        
    except Exception as e:
        print(f"Error counting films by keyword '{keyword}': {e}")
        return 0

def count_films_by_actor(actor_keyword):
    """
    Count total number of films matching actor keyword.
    Args:
        actor_keyword (str): Part of actor's name or surname
    Returns:
        int: Total number of matching films
    """
    try:
        like_keyword = f"%{actor_keyword.lower()}%"
        query = '''
            SELECT COUNT(*) ct
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            WHERE LOWER(a.first_name) LIKE %s OR LOWER(a.last_name) LIKE %s
        '''
        result= get_from_mysql(query, (like_keyword, like_keyword))
        return result[0]['ct'] if result else 0

    except Exception as e:
        print(f"Error counting films by actor '{actor_keyword}': {e}")
        return 0

def find_films_by_actor_with_genre(actor_keyword, limit=10, skip=0):
    """
    Find films by part of actor's name or surname, with genre and year, with pagination.
    Args:
        actor_keyword (str): Part of actor's name or surname (case-insensitive)
        limit (int): Number of results per page
        skip (int): Offset for pagination
    Returns:
        list: List of film dictionaries with actor, title, year, genre
    """
    try:
        like_keyword = f"%{actor_keyword.lower()}%"
        query = '''
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
        '''
        results, headers = get_head_row_from_mysql(query, (like_keyword, like_keyword, limit, skip))
        return results, headers
    except Exception as e:
        print(f"Error searching films by actor '{actor_keyword}': {e}")
        return []

# Update get_year_range function to return tuple instead of dict
def get_year_range():
    """
    Get the minimum and maximum year from MySQL films table.
    
    Returns:
        tuple: (min_year, max_year) or None if error
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
        print(f"Error getting year range: {e}")
        return None



def close_mysql_connection():
    """
    Close ALL connection and clear cache.
    """
    close_all_connections()