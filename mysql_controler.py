# =====================================================
# MYSQL FUNCTIONS (Films Data)
# =====================================================

import pandas as pd
import pymysql
from db import initialize_mysql, initialize_mysql_engine
from mongo_controler import log_search_query

# Установка отображения всех строк и столбцов
pd.set_option('display.max_rows', None)     # Показывать все строки
pd.set_option('display.max_columns', None)  # Показывать все столбцы
pd.set_option('display.width', 0)           # Автоматическая ширина
pd.set_option('display.max_colwidth', None) # Показывать весь текст в ячейках

def get_pandas_dataframe_from_mysql(query, params=None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a Pandas DataFrame.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the SQL query
    
    Returns:
        pd.DataFrame: DataFrame with results
    """
    try:
        
        engine = initialize_mysql_engine()
        # connection = initialize_mysql()
        # cursor = connection.cursor(pymysql.cursors.DictCursor)
        # cursor.execute(query, params)
        
        # results = cursor.fetchall()
        # columns = [i[0] for i in cursor.description]
        # df = pd.DataFrame(results, columns=columns)
        
        # cursor.close()
        
        return pd.read_sql_query(query, engine, params=params)

        # return df, results
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()

def get_from_mysql(query, params=None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a Pandas DataFrame.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the SQL query
    
    Returns:
        pd.DataFrame: DataFrame with results
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

def count_films_by_keyword(keyword):
    """
    Count total number of films matching keyword.
    
    Args:
        keyword (str): Keyword to search for
    
    Returns:
        int: Total number of matching films
    """
    try:
        # connection = initialize_mysql()
        # cursor = connection.cursor()
        
        query = """
        SELECT COUNT(*) as total
        FROM film_text
        WHERE title LIKE %s
        """
        
        search_pattern = f"%{keyword}%"
        # cursor.execute(sql, (search_pattern,))
        
        # result = cursor.fetchone()
        # cursor.close()
        results = get_pandas_dataframe_from_mysql(query, (search_pattern,))
        
        if not results.empty:
            return results.iloc[0]['total']
        else:
            return 0
        
    except Exception as e:
        print(f"Error counting films by keyword '{keyword}': {e}")
        return 0

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
        # connection = initialize_mysql()
        # cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # найти первые 10 фильмов, где в названии встречается ключевое слово (например, 'Love')
        # sql = """
        # SELECT title, description
        # FROM film_text
        # WHERE title LIKE %s
        # LIMIT %s OFFSET %s
        # """
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
        
        # query =f'''
        #     SELECT ft.title, ft.description, f.release_year, c.name AS genre
        #     FROM film_text ft
        #     JOIN film f ON ft.film_id = f.film_id
        #     JOIN film_category fc ON f.film_id = fc.film_id
        #     JOIN category c ON fc.category_id = c.category_id
        #     WHERE LOWER(ft.title) LIKE '%{keyword.lower()}%'
        #     LIMIT {limit} OFFSET {offset};
        # '''

        
        params=(search_pattern, limit, skip)
        df_results = get_pandas_dataframe_from_mysql(query, params)
        # cursor.execute(query, (search_pattern, limit, skip))
        # results = cursor.fetchall()
        # kolonki = [i[0] for i in cursor.description]
        # df = pd.DataFrame(results, columns=kolonki)
        # cursor.close()
        
        # Log the search
        log_search_query(keyword, 'keyword', len(df_results))
        
        return df_results
        
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
        # connection = initialize_mysql()
        # cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        if genre and year_from and year_to:
            # найти фильмы по жанру и диапазону годов
            query = """
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
            """
            params = (genre, year_from, year_to, limit, skip)
            # cursor.execute(sql, (genre, year_from, year_to, limit, skip))
            
        elif genre:
            # найти первые 10 фильмов по жанру (например 'Comedy')
            query = """
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s
            LIMIT %s OFFSET %s
            """
            params = (genre, limit, skip)
            # cursor.execute(sql, (genre, limit, skip))
            
        elif year_from and year_to:
            # найти первые 10 фильмов по диапазону годов (например 2005-2012)
            query = """
            SELECT title, release_year
            FROM film
            WHERE release_year BETWEEN %s AND %s
            LIMIT %s OFFSET %s
            """
            params = (year_from, year_to, limit, skip)
            # cursor.execute(sql, (year_from, year_to, limit, skip))
            
        else:
            # если никаких критериев не указано, возвращаем пустой результат
            return []
        
        # results = cursor.fetchall()
        # cursor.close()
        
        # Log the search
        search_criteria = f"genre:{genre}, years:{year_from}-{year_to}"
        # 
        
        df_results = get_pandas_dataframe_from_mysql(query, params)
        log_search_query(search_criteria, 'genre_year', len(df_results))

        return df_results
        
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
        # connection = initialize_mysql()
        # cursor = connection.cursor()
        
        # вывести все категории
        query = """
        SELECT name AS genre
        FROM category
        """
        # cursor.execute(sql)
        
        # results = cursor.fetchall()
        # cursor.close()
        
        # # Extract genre names from tuples
        # genres = [row[0] for row in results]
        
        df_results = get_pandas_dataframe_from_mysql(query)
        return df_results["genre"].tolist()
        
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
        # connection = initialize_mysql()
        # cursor = connection.cursor()
        
        # вывести мин и мах года выпуска фильма
        query = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM film
        """
        # cursor.execute(sql)
        
        # result = cursor.fetchone()
        # cursor.close()
        df_results = get_pandas_dataframe_from_mysql(query)

        if not df_results.empty:
            return {
                'min_year': df_results.iloc[0]['min_year'],
                'max_year': df_results.iloc[0]['max_year']
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
        # connection = initialize_mysql()
        # cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Try to find by ID first, then by title
        query = "SELECT * FROM films WHERE id = %s OR title = %s LIMIT 1"
        # cursor.execute(sql, (key, key))
        
        # result = cursor.fetchone()
        # cursor.close()
        params = (key, key)
        df_results = get_pandas_dataframe_from_mysql(query, params)
        # log_search_query(search_criteria, 'genre_year', len(results))
        return df_results.iloc[0].to_dict() if not df_results.empty else None
        
    except Exception as e:
        print(f"Error finding film by key '{key}': {e}")
        return None
    

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
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error counting films by keyword '{keyword}': {e}")
        return 0



