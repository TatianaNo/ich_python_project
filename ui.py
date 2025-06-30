import logging

logger = logging.getLogger(__name__)

# UI module for user interaction - only user interface logic
from formatter import (
    clear_screen,
    format_table,
    format_title,
    format_menu_option,
    format_section_header,
    format_border,
    format_error,
    format_info,
    format_warning,
    format_prompt,
    format_wait_prompt,
    format_pagination_info,
    format_pagination_prompt,
)
from mongo_controler import get_last_queries, log_search_query, get_popular_queries
from mysql_controler import (
    close_mysql_connection,
    count_films_by_actor,
    count_films_by_genre,
    count_films_by_keyword,
    find_films_by_actor_with_genre,
    find_films_by_criteria,
    find_films_by_keyword,
    get_all_genres,
    get_year_range,
)


menu = {
    "1": "Поиск фильма по названию",
    "2": "Поиск фильма по жанру и диапазону годов выпуска",
    "3": "Поиск фильма по актеру",
    "4": "Просмотр популярных запросов",
    "5": "Просмотр последних (уникальных) запросов",
    "0": "Выход",
}


def show_menu():
    """
    Display the main menu to the user in the console.
    """
    clear_screen()
    print(format_title("СИСТЕМА ПОИСКА ФИЛЬМОВ"))
    print(format_section_header("Выберите действие"))
    for key, value in menu.items():
        print(format_menu_option(key, value))
    print(format_border())


def get_menu_choice():
    """
    Prompt the user to select a menu option and validate the input.
    Returns:
        str: The selected menu option key.
    """
    while True:
        choice = input(format_prompt("Введите номер действия:")).strip()
        if choice in menu.keys():
            return choice
        else:
            print(format_error("Неверный ввод. Попробуйте снова."))


def get_year_range_choice():
    """
    Prompt the user to select a year range for film search.
    Returns:
        dict: Dictionary with 'year_from' and 'year_to'.
    """
    print(format_section_header("Поиск по диапазону годов"))
    year_info = get_year_range()
    min_year, max_year = year_info["min_year"], year_info["max_year"]
    if year_info:
        print(format_info(f"Доступный диапазон годов: {min_year} - {max_year}"))
    year_from = input(
        format_prompt(f"Введите начальный год (мин: {min_year}):")
    ).strip()
    year_to = input(format_prompt(f"Введите конечный год (макс: {max_year}):")).strip()
    try:
        year_from = int(year_from) if year_from else min_year
        year_to = int(year_to) if year_to else max_year
        if year_from and year_to and year_from > year_to:
            print(format_error("Начальный год не может быть больше конечного года!"))
            return get_year_range_choice()
        return {"year_from": year_from, "year_to": year_to}
    except ValueError as e:
        logger.error("Ошибка преобразования года:", e)
        print(format_error("Неверный формат года. Введите числовое значение."))
        return get_year_range_choice()


def search_film_by_title():
    """
    Search for films by title keyword and display paginated results.
    Prompts the user for a keyword and handles pagination and logging.
    """
    keyword = input(
        format_prompt("Введите ключевое слово для поиска в названии фильма:")
    ).strip()
    if not keyword:
        print(format_error("Ключевое слово не может быть пустым!"))
        return
    offset = 0
    total = count_films_by_keyword(keyword)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        input(format_wait_prompt())
        return
    while True:
        row, head = find_films_by_keyword(keyword, limit=10, skip=offset)
        if not row:
            print(format_info("Больше результатов нет."))
            input(format_wait_prompt())
            break
        print(format_table(row, head))
        print(format_pagination_info(offset // 10 + 1, total, 10))
        if offset + 10 >= total:
            print(format_info("Это все результаты."))
            input(format_wait_prompt())
            break
        if input(format_pagination_prompt()).strip().lower() not in [
            "y",
            "yes",
            "да",
            "д",
        ]:
            break
        offset += 10
    log_search_query(keyword, "title", total)
    input(format_wait_prompt())


def search_film_by_genre_and_year():
    """
    Search for films by genre and year range, display paginated results.
    Prompts the user to select a genre and year range, handles pagination and logging.
    """
    genres = get_all_genres()
    if not genres:
        print(format_error("Не удалось получить список жанров."))
        input(format_wait_prompt())
        return
    print(format_info("Доступные жанры:"))
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    genre_input = input(format_prompt("Введите номер выбранного жанра:")).strip()
    if not genre_input.isdigit:
        print(format_error("Введите номер, а не строку."))
        input(format_wait_prompt())
        return
    if int(genre_input) > len(genres):
        print(format_error("Выберите номер из списка."))
        input(format_wait_prompt())
        return
    genre = genres[int(genre_input) - 1]
    print(format_prompt(f"Выбраный жанр: {genre} "))
    year = get_year_range_choice()
    offset = 0
    year["genre"] = genre
    total = count_films_by_genre(year)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        input(format_wait_prompt())
        return
    while True:
        films, headers = find_films_by_criteria(year, limit=10, skip=offset)
        if not films:
            print(format_info("Больше результатов нет."))
            input(format_wait_prompt())
            break
        formatted_lines = format_table(films, headers)
        print(formatted_lines)
        print(format_pagination_info(offset // 10 + 1, total, 10))
        if offset + 10 >= total:
            print(format_info("Это все результаты."))
            input(format_wait_prompt())
            break
        if input(format_pagination_prompt()).strip().lower() not in [
            "y",
            "yes",
            "да",
            "д",
        ]:
            break
        offset += 10
    log_search_query(
        f"{genre} {year["year_from"]}-{year["year_to"]}", "genre_year", total
    )


def search_film_by_actor():
    """
    Search for films by actor name or surname, display paginated results.
    Prompts the user for part of an actor's name, handles pagination and logging.
    """
    keyword = input(format_prompt("Введите часть имени или фамилии актёра:")).strip()
    if not keyword:
        print(format_error("Поле не может быть пустым!"))
        input(format_wait_prompt())
        return
    offset = 0
    total = count_films_by_actor(keyword)
    if total == 0:
        print(format_error("Фильмы не найдены."))
        input(format_wait_prompt())
        return
    while True:
        films, headers = find_films_by_actor_with_genre(keyword, limit=10, skip=offset)
        if not films:
            print(format_info("Больше результатов нет."))
            break
        films_table = format_table(films, headers)
        print(films_table)
        print(format_pagination_info(offset // 10 + 1, total, 10))
        if offset + 10 >= total:
            print(format_info("Это все результаты."))
            input(format_wait_prompt())
            break
        if input(format_pagination_prompt()).strip().lower() not in [
            "y",
            "yes",
            "да",
            "д",
        ]:
            break
        offset += 10
    log_search_query(keyword, "actor", total)


def display_popular_queries(limit=5):
    """
    Display the most popular search queries using the formatter.
    Args:
        limit (int): Number of popular queries to display.
    """
    print(format_title(f"СТАТИСТИКА ПОПУЛЯРНЫХ {limit} ПОИСКОВЫХ ЗАПРОСОВ", 60))
    popular = get_popular_queries(limit=5)
    print(format_table(popular, ["_id", "count", "search_type", "last_searched"]))
    input(format_wait_prompt())


def show_recent_queries(limit=5):
    """
    Display the most recent unique search queries using the formatter.
    Args:
        limit (int): Number of recent queries to display.
    """
    recent = get_last_queries(limit)
    print(format_title(f"СТАТИСТИКА ПОСЛЕДНИХ {limit} УНИКАЛЬНЫХ ЗАПРОСОВ", 60))
    print(format_table(recent, ["_id", "count", "search_type", "last_searched"]))
    input(format_wait_prompt())


def show_exit_message():
    """
    Display an exit message and close the MySQL connection.
    """
    print(format_info("Закрытие соединения с базой данных..."))
    print(format_warning("До свидания!"))
    close_mysql_connection()
