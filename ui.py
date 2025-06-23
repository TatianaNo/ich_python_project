# UI module for user interaction - only user interface logic
from formatter import (
    clear_screen, format_title, format_menu_option, format_section_header,
    format_film_title, format_film_detail, format_query_item, format_border,
    format_error, format_success, format_info, format_warning, 
    format_prompt, format_wait_prompt, format_films_list,
    format_popular_queries_section, format_recent_queries_section,
    format_general_stats_section, format_query_detail,
    format_pagination_info, format_pagination_prompt
)

menu = {
    "1": "Поиск по ключевому слову", 
    "2": "Поиск по жанру",
    "3": "Поиск по диапазону годов",
    "4": "Посмотреть популярные запросы",
    "9": "Выход"
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
    from mysql_connector import get_all_genres
    
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
    from mysql_connector import get_year_range
    
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

def search_films_by_genre_with_pagination(genre):
    """Search films by genre with pagination support."""
    from mysql_connector import find_films_by_genre, count_films_by_genre
    from log_writer import log_search_query
    
    # Get total count first
    total_results = count_films_by_genre(genre)
    
    if total_results == 0:
        print(format_error(f"Фильмы жанра '{genre}' не найдены."))
        input(format_wait_prompt())
        return
    
    current_page = 1
    results_per_page = 10
    
    while True:
        # Calculate offset
        offset = (current_page - 1) * results_per_page
        
        # Get films for current page
        films = find_films_by_genre(genre, limit=results_per_page, skip=offset)
        
        if not films:
            print(format_info("Больше результатов нет."))
            break
        
        # Display pagination info
        print(format_pagination_info(current_page, total_results, results_per_page))
        
        # Display films
        formatted_lines = format_films_list(films)
        for line in formatted_lines:
            print(line)
        
        # Check if there are more results
        if offset + results_per_page >= total_results:
            print(format_info("Это все результаты."))
            break
        
        # Ask user if they want to continue
        choice = input(format_pagination_prompt()).strip().lower()
        if choice not in ['y', 'yes', 'да', 'д']:
            break
            
        current_page += 1
    
    # Log the search
    log_search_query(genre, 'genre', total_results)
    
    input(format_wait_prompt())

def search_films_by_year_range_with_pagination(year_params):
    """Search films by year range with pagination support."""
    from mysql_connector import find_films_by_year_range, count_films_by_year_range
    from log_writer import log_search_query
    
    year_from = year_params.get('year_from')
    year_to = year_params.get('year_to')
    
    # Get total count first
    total_results = count_films_by_year_range(year_from, year_to)
    
    if total_results == 0:
        year_range_str = f"{year_from or 'начало'} - {year_to or 'конец'}"
        print(format_error(f"Фильмы в диапазоне годов {year_range_str} не найдены."))
        input(format_wait_prompt())
        return
    
    current_page = 1
    results_per_page = 10
    
    while True:
        # Calculate offset
        offset = (current_page - 1) * results_per_page
        
        # Get films for current page
        films = find_films_by_year_range(year_from, year_to, limit=results_per_page, skip=offset)
        
        if not films:
            print(format_info("Больше результатов нет."))
            break
        
        # Display pagination info
        print(format_pagination_info(current_page, total_results, results_per_page))
        
        # Display films
        formatted_lines = format_films_list(films)
        for line in formatted_lines:
            print(line)
        
        # Check if there are more results
        if offset + results_per_page >= total_results:
            print(format_info("Это все результаты."))
            break
        
        # Ask user if they want to continue
        choice = input(format_pagination_prompt()).strip().lower()
        if choice not in ['y', 'yes', 'да', 'д']:
            break
            
        current_page += 1
    
    # Log the search
    year_range_str = f"{year_from or 'начало'}-{year_to or 'конец'}"
    log_search_query(year_range_str, 'year_range', total_results)
    
    input(format_wait_prompt())

def display_films(films):
    """Display a list of films using formatter."""
    formatted_lines = format_films_list(films)
    for line in formatted_lines:
        print(line)
    input(format_wait_prompt())

def search_films_with_pagination(keyword):
    """Search films with pagination support."""
    from mysql_connector import find_films_by_keyword, count_films_by_keyword
    from log_writer import log_search_query
    
    # Get total count first
    total_results = count_films_by_keyword(keyword)
    
    if total_results == 0:
        print(format_error("Фильмы не найдены."))
        input(format_wait_prompt())
        return
    
    current_page = 1
    results_per_page = 10
    
    while True:
        # Calculate offset
        offset = (current_page - 1) * results_per_page
        
        # Get films for current page
        films = find_films_by_keyword(keyword, limit=results_per_page, skip=offset)
        
        if not films:
            print(format_info("Больше результатов нет."))
            break
        
        # Display pagination info
        print(format_pagination_info(current_page, total_results, results_per_page))
        
        # Display films
        formatted_lines = format_films_list(films)
        for line in formatted_lines:
            print(line)
        
        # Check if there are more results
        if offset + results_per_page >= total_results:
            print(format_info("Это все результаты."))
            break
        
        # Ask user if they want to continue
        choice = input(format_pagination_prompt()).strip().lower()
        if choice not in ['y', 'yes', 'да', 'д']:
            break
            
        current_page += 1
    
    # Log the search (log total results found)
    log_search_query(keyword, 'keyword', total_results)
    
    input(format_wait_prompt())

def display_popular_queries():
    """Display popular or recent queries using log_stats and formatter."""
    from log_stats import get_popular_queries, get_recent_queries, get_search_stats_from_file
    
    print(format_title("СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ", 60))
    
    # Get and display popular queries
    popular = get_popular_queries(5)
    popular_lines = format_popular_queries_section(popular)
    for line in popular_lines:
        print(line)
    
    # Get and display recent queries
    recent = get_recent_queries(5)
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

def show_exit_message():
    """Display exit message."""
    print(format_info("Закрытие соединения с базой данных..."))
    print(format_warning("До свидания!"))

def ask_continue():
    """Ask user if they want to continue with more results."""
    choice = input(format_prompt("Показать больше результатов? (y/n):")).strip().lower()
    return choice in ['y', 'yes', 'да', 'д']
