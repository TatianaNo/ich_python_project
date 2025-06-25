# UI module for user interaction - only user interface logic
from formatter import (
    clear_screen, format_title, format_menu_option, format_section_header,
    format_border,
    format_error, format_info, format_warning, 
    format_prompt, format_wait_prompt, format_films_list,
    format_popular_queries_section, format_recent_queries_section,
    format_general_stats_section,
    format_pagination_info, format_pagination_prompt
)

from mysql_connector import close_mysql_connection, find_films_by_keyword, count_films_by_keyword
from mysql_connector import get_all_genres
from mysql_connector import get_year_range
from mysql_connector import get_all_genres, get_year_range, find_films_by_criteria, count_films_by_genre
from mysql_connector import find_films_by_actor_with_genre, count_films_by_actor
from log_writer import log_search_query
from log_writer import close_mongo_connection, log_search_query
from log_stats import get_popular_queries, show_recent_queries, get_search_stats_from_file


menu = {
    "1": "Поиск фильма по названию",
    "2": "Поиск фильма по жанру и диапазону годов выпуска",
    "3": "Поиск фильма по актеру",
    "4": "Просмотр популярных запросов",
    "5": "Просмотр последних (уникальных) запросов",
    "0": "Выход"
}

def show_menu():
    """Display the main menu to the user."""
    clear_screen()
    print(format_title("СИСТЕМА ПОИСКА ФИЛЬМОВ"))
    print(format_section_header("Выберите действие"))
    for key, value in menu.items():
        print(format_menu_option(key, value))
    print(format_border())

def get_menu_choice():
    """Get menu choice from user with validation."""
    while True:
        choice = input(format_prompt("Введите номер действия:")).strip()
        if choice in menu.keys():
            return choice
        else:
            print(format_error("Неверный ввод. Попробуйте снова."))

def get_search_keyword():
    """Get search keyword from user."""
    keyword = input(format_prompt("Введите ключевое слово для поиска:")).strip()
    if not keyword:
        print(format_error("Ключевое слово не может быть пустым!"))
        return get_search_keyword()
    return keyword

def get_genre_choice():
    """Get genre choice from user with list of available genres."""
    
    print(format_section_header("Поиск по жанру"))
    
    # Get all available genres
    genres = get_all_genres()
    if not genres:
        print(format_error("Не удалось получить список жанров."))
        return None
    
    # Display available genres
    print(format_info("Доступные жанры:"))
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    
    # Get user choice
    while True:
        choice = input(format_prompt("Введите название жанра:")).strip()
        if not choice:
            print(format_error("Жанр не может быть пустым!"))
            continue
        
        # Check if genre exists (case insensitive)
        for genre in genres:
            if choice.lower() == genre.lower():
                return genre
        
        print(format_error(f"Жанр '{choice}' не найден. Попробуйте снова."))

def get_year_range_choice():
    """Get year range choice from user with available range info."""
    
    print(format_section_header("Поиск по диапазону годов"))
    
    # Get available year range
    year_info = get_year_range()
    min_year, max_year = None, None
    if year_info:
        min_year, max_year = year_info
        print(format_info(f"Доступный диапазон годов: {min_year} - {max_year}"))
    
    # Get year range from user
    year_from = input(format_prompt("Введите начальный год:")).strip()
    year_to = input(format_prompt("Введите конечный год:")).strip()
    
    # Validate years
    try:
        year_from = int(year_from) if year_from else None
        year_to = int(year_to) if year_to else None
        
        if year_from is None and year_to is None:
            print(format_error("Необходимо указать хотя бы один год!"))
            return get_year_range_choice()
        
        # Validate that years are within available range
        if year_info:
            if year_from and (year_from < min_year or year_from > max_year):
                print(format_error(f"Начальный год должен быть в диапазоне {min_year} - {max_year}!"))
                return get_year_range_choice()
            
            if year_to and (year_to < min_year or year_to > max_year):
                print(format_error(f"Конечный год должен быть в диапазоне {min_year} - {max_year}!"))
                return get_year_range_choice()
            
        # Validate range
        if year_from and year_to and year_from > year_to:
            print(format_error("Начальный год не может быть больше конечного года!"))
            return get_year_range_choice()
        
        return {'year_from': year_from, 'year_to': year_to}
    except ValueError:
        print(format_error("Неверный формат года. Введите числовое значение."))
        return get_year_range_choice()

def search_film_by_title():
    
    keyword = input(format_prompt("Введите ключевое слово для поиска в названии фильма:")).strip()
    if not keyword:
        print(format_error("Ключевое слово не может быть пустым!"))
        return
    offset = 0
    total = count_films_by_keyword(keyword)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        return
    while True:
        films = find_films_by_keyword(keyword, limit=10, skip=offset)
        if not films:
            print(format_info("Больше результатов нет."))
            break
        formatted_lines = format_films_list(films)
        for line in formatted_lines:
            print(line)
        print(format_pagination_info(offset//10+1, total, 10))
        if offset+10 >= total:
            print(format_info("Это все результаты."))
            break
        if input(format_pagination_prompt()).strip().lower() not in ["y", "yes", "да", "д"]:
            break
        offset += 10
    log_search_query(keyword, 'title', total)

def search_film_by_genre_and_year():
    genres = get_all_genres()
    if not genres:
        print(format_error("Не удалось получить список жанров."))
        return
    print(format_info("Доступные жанры:"))
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    year_info = get_year_range()
    if not year_info:
        print(format_error("Не удалось получить диапазон годов."))
        return
    min_year, max_year = year_info
    print(format_info(f"Доступный диапазон годов: {min_year} - {max_year}"))
    genre_input = input(format_prompt("Введите название жанра:")).strip()
    if genre_input not in genres:
        print(format_error("Жанр не найден."))
        return
    try:
        year_from = int(input(format_prompt(f"Введите начальный год ({min_year}):")).strip())
        year_to = int(input(format_prompt(f"Введите конечный год ({max_year}):")).strip())
    except ValueError:
        print(format_error("Годы должны быть числами."))
        return
    if not (min_year <= year_from <= max_year and min_year <= year_to <= max_year and year_from <= year_to):
        print(format_error("Введён некорректный диапазон годов."))
        return
    offset = 0
    total = count_films_by_genre(genre_input)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        return
    while True:
        films = find_films_by_criteria(genre=genre_input, year_from=year_from, year_to=year_to, limit=10, skip=offset)
        if not films:
            print(format_info("Больше результатов нет."))
            break
        formatted_lines = format_films_list(films)
        for line in formatted_lines:
            print(line)
        print(format_pagination_info(offset//10+1, total, 10))
        if offset+10 >= total:
            print(format_info("Это все результаты."))
            break
        if input(format_pagination_prompt()).strip().lower() not in ["y", "yes", "да", "д"]:
            break
        offset += 10
    log_search_query(f"{genre_input} {year_from}-{year_to}", 'genre_year', total)

def search_film_by_actor():
    keyword = input(format_prompt("Введите часть имени или фамилии актёра:")).strip()
    if not keyword:
        print(format_error("Поле не может быть пустым!"))
        return
    offset = 0
    total = count_films_by_actor(keyword)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        return
    while True:
        films = find_films_by_actor_with_genre(keyword, limit=10, skip=offset)
        if not films:
            print(format_info("Больше результатов нет."))
            break
        for i, film in enumerate(films, 1+offset):
            print(f"{i}. {film['film_title']} ({film['release_year']}) | Жанр: {film['genre']} | Актёр: {film['actor_name']}")
        print(format_pagination_info(offset//10+1, total, 10))
        if offset+10 >= total:
            print(format_info("Это все результаты."))
            break
        if input(format_pagination_prompt()).strip().lower() not in ["y", "yes", "да", "д"]:
            break
        offset += 10
    log_search_query(keyword, 'actor', total)

def display_films(films):
    """Display a list of films using formatter."""
    formatted_lines = format_films_list(films)
    for line in formatted_lines:
        print(line)
    input(format_wait_prompt())

def display_popular_queries():
    """Display popular or recent queries using log_stats and formatter."""
    
    print(format_title("СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ", 60))
    
    # Get and display popular queries
    popular = get_popular_queries(5)
    popular_lines = format_popular_queries_section(popular)
    for line in popular_lines:
        print(line)
    
    # Get and display recent queries
    recent = show_recent_queries(5)
    recent_lines = format_recent_queries_section(recent)
    for line in recent_lines:
        print(line)
    
    # Get and display general stats if available
    try:
        stats = get_search_stats_from_file()
        stats_lines = format_general_stats_section(stats)
        for line in stats_lines:
            print(line)
    except:
        pass
    
    print(format_border(60))
    input(format_wait_prompt())

def show_recent_queries(limit=10):
    """Get recent unique queries from logs."""
    shown = set()
    recent = show_recent_queries(limit)
    for q in recent:
        if q.get('query') not in shown:
            print(q.get('query'))
            shown.add(q.get('query'))

def show_exit_message():
    """Display exit message."""
    print(format_info("Закрытие соединения с базой данных..."))
    print(format_warning("До свидания!"))
    close_mysql_connection()
    close_mongo_connection()


def ask_continue():
    """Ask user if they want to continue with more results."""
    choice = input(format_prompt("Показать больше результатов? (y/n):")).strip().lower()
    return choice in ['y', 'yes', 'да', 'д']
