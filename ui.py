# UI module for user interaction
import os

# ANSI color codes
BLUE = '\033[94m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

menu = {
    "1": "Поиск по ключевому слову", 
    "2": "Поиск по жанру и диапазону годов",
    "3": "Посмотреть популярные запросы",
    "9": "Выход"
}

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Display the main menu to the user."""
    clear_screen()
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{YELLOW}{BOLD}СИСТЕМА ПОИСКА ФИЛЬМОВ{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    print(f"{GREEN}Выберите действие:{RESET}")
    for key, value in menu.items():
        print(f"  {YELLOW}{key}.{RESET} {value}")
    print(f"{BLUE}{'='*50}{RESET}")

def get_menu_choice():
    """Get menu choice from user with validation."""
    while True:
        choice = input(f"\n{YELLOW}Введите номер действия:{RESET} ").strip()
        if choice in menu.keys():
            return choice
        else:
            print(f"{RED}Неверный ввод. Попробуйте снова.{RESET}")

def get_search_keyword():
    """Get search keyword from user."""
    keyword = input(f"{BLUE}Введите ключевое слово для поиска:{RESET} ").strip()
    if not keyword:
        print(f"{RED}Ключевое слово не может быть пустым!{RESET}")
        return get_search_keyword()
    return keyword

def get_genre_and_year_range():
    """Get genre and year range from user."""
    print(f"\n{BLUE}Поиск по жанру и диапазону годов:{RESET}")
    
    # Get genre
    genre = input(f"{YELLOW}Введите жанр (или нажмите Enter для пропуска):{RESET} ").strip()
    
    # Get year range
    year_from = input(f"{YELLOW}Введите начальный год (или нажмите Enter для пропуска):{RESET} ").strip()
    year_to = input(f"{YELLOW}Введите конечный год (или нажмите Enter для пропуска):{RESET} ").strip()
    
    # Validate years
    if year_from:
        try:
            year_from = int(year_from)
        except ValueError:
            print(f"{RED}Неверный начальный год. Используется значение по умолчанию.{RESET}")
            year_from = None
    else:
        year_from = None
        
    if year_to:
        try:
            year_to = int(year_to)
        except ValueError:
            print(f"{RED}Неверный конечный год. Используется значение по умолчанию.{RESET}")
            year_to = None
    else:
        year_to = None
    
    return {
        'genre': genre if genre else None,
        'year_from': year_from,
        'year_to': year_to
    }

def display_film(film):
    """Display a single film information."""
    if not film:
        print("Фильм не найден.")
        return
    
    print("\n" + "="*50)
    print(f"Название: {film.get('title', 'Не указано')}")
    print(f"Год: {film.get('year', 'Не указан')}")
    print(f"Жанр: {film.get('genre', 'Не указан')}")
    print(f"Рейтинг: {film.get('rating', 'Не указан')}")
    print(f"Описание: {film.get('description', 'Не указано')}")
    print("="*50)

def display_films(films):
    """Display a list of films."""
    if not films:
        print(f"\n{RED}Фильмы не найдены.{RESET}")
        input(f"\n{YELLOW}Нажмите Enter для продолжения...{RESET}")
        return
    
    print(f"\n{GREEN}Найдено {len(films)} фильм(ов):{RESET}")
    for i, film in enumerate(films, 1):
        print(f"\n{YELLOW}{i}.{RESET} {BOLD}{film.get('title', 'Не указано')}{RESET} {BLUE}({film.get('year', 'Не указан')}){RESET}")
        print(f"   Жанр: {film.get('genre', 'Не указан')}")
        print(f"   Рейтинг: {film.get('rating', 'Не указан')}")
    
    input(f"\n{YELLOW}Нажмите Enter для продолжения...{RESET}")

def display_popular_queries():
    """Display popular or recent queries from MongoDB or local file."""
    from db import get_popular_queries, get_recent_queries, get_search_stats_from_file
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}{BOLD}СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Show popular queries
    print(f"\n{GREEN}Топ-5 популярных запросов:{RESET}")
    popular = get_popular_queries(5)
    
    if popular:
        for i, query in enumerate(popular, 1):
            # Handle both MongoDB and file formats
            if isinstance(query, dict):
                if '_id' in query:  # MongoDB format
                    query_text = query['_id']
                    count = query['count']
                    search_type = query.get('search_type', 'unknown')
                    last_searched = query.get('last_searched', 'unknown')
                    if hasattr(last_searched, 'strftime'):
                        last_searched_str = last_searched.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_searched_str = str(last_searched)
                else:  # File format
                    query_text = query.get('query', 'unknown')
                    count = query.get('count', 0)
                    search_type = 'unknown'
                    last_searched_str = 'unknown'
                
                print(f"{YELLOW}{i}.{RESET} '{BLUE}{query_text}{RESET}' - {count} раз(а)")
                if search_type != 'unknown':
                    print(f"   Тип: {search_type}, Последний поиск: {last_searched_str}")
                else:
                    print(f"   Количество запросов: {count}")
    else:
        print(f"   {RED}Нет данных о популярных запросах{RESET}")
    
    # Show recent queries
    print(f"\n{GREEN}Последние 5 запросов:{RESET}")
    recent = get_recent_queries(5)
    
    if recent:
        for i, query in enumerate(recent, 1):
            query_text = query.get('query', 'unknown')
            search_type = query.get('search_type', 'unknown')
            results_count = query.get('results_count', 0)
            timestamp = query.get('timestamp', 'unknown')
            
            # Handle timestamp formatting
            if hasattr(timestamp, 'strftime'):
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                timestamp_str = str(timestamp)
            
            print(f"{YELLOW}{i}.{RESET} '{BLUE}{query_text}{RESET}' - {timestamp_str}")
            print(f"   Тип: {search_type}, Результатов: {results_count}")
    else:
        print(f"   {RED}Нет данных о последних запросах{RESET}")
    
    # Show general stats if using file storage
    try:
        stats = get_search_stats_from_file()
        if stats['total_searches'] > 0:
            print(f"\n{GREEN}Общая статистика:{RESET}")
            print(f"   Всего поисков: {stats['total_searches']}")
            if stats['search_types']:
                print("   По типам:")
                for search_type, count in stats['search_types'].items():
                    print(f"     - {search_type}: {count}")
    except:
        pass
    
    print(f"{BLUE}{'='*60}{RESET}")
    input(f"\n{YELLOW}Нажмите Enter для продолжения...{RESET}")

def show_exit_message():
    """Display exit message."""
    print(f"\n{BLUE}Закрытие соединения с базой данных...{RESET}")
    print(f"{YELLOW}До свидания!{RESET}")

def ask_continue():
    """Ask user if they want to continue with more results."""
    choice = input("\nПоказать больше результатов? (y/n): ").strip().lower()
    return choice in ['y', 'yes', 'да', 'д']
