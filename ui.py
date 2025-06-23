# UI module for user interaction

menu = {
    "1": "Поиск по ключевому слову", 
    "2": "Поиск по жанру и диапазону годов",
    "3": "Посмотреть популярные запросы",
    "9": "Выход"
}

def show_menu():
    """Display the main menu to the user."""
    print("\nВыберите действие:")
    for key, value in menu.items():
        print(f"{key}. {value}")

def get_menu_choice():
    """Get menu choice from user with validation."""
    while True:
        choice = input("\nВведите номер действия: ").strip()
        if choice in menu.keys():
            return choice
        else:
            print("Неверный ввод. Попробуйте снова.")

def get_search_keyword():
    """Get search keyword from user."""
    keyword = input("Введите ключевое слово для поиска: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return get_search_keyword()
    return keyword

def get_genre_and_year_range():
    """Get genre and year range from user."""
    print("\nПоиск по жанру и диапазону годов:")
    
    # Get genre
    genre = input("Введите жанр (или нажмите Enter для пропуска): ").strip()
    
    # Get year range
    year_from = input("Введите начальный год (или нажмите Enter для пропуска): ").strip()
    year_to = input("Введите конечный год (или нажмите Enter для пропуска): ").strip()
    
    # Validate years
    if year_from:
        try:
            year_from = int(year_from)
        except ValueError:
            print("Неверный начальный год. Используется значение по умолчанию.")
            year_from = None
    else:
        year_from = None
        
    if year_to:
        try:
            year_to = int(year_to)
        except ValueError:
            print("Неверный конечный год. Используется значение по умолчанию.")
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
        print("\nФильмы не найдены.")
        return
    
    print(f"\nНайдено {len(films)} фильм(ов):")
    for i, film in enumerate(films, 1):
        print(f"\n{i}. {film.get('title', 'Не указано')} ({film.get('year', 'Не указан')})")
        print(f"   Жанр: {film.get('genre', 'Не указан')}")
        print(f"   Рейтинг: {film.get('rating', 'Не указан')}")

def display_popular_queries():
    """Display popular or recent queries from MongoDB."""
    from db import get_popular_queries, get_recent_queries
    
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ")
    print("="*60)
    
    # Show popular queries
    print("\n🔥 Топ-5 популярных запросов:")
    popular = get_popular_queries(5)
    
    if popular:
        for i, query in enumerate(popular, 1):
            print(f"{i}. '{query['_id']}' - {query['count']} раз(а)")
            print(f"   Тип: {query['search_type']}, Последний поиск: {query['last_searched'].strftime('%Y-%m-%d %H:%M')}")
    else:
        print("   Нет данных о популярных запросах")
    
    # Show recent queries
    print("\n⏰ Последние 5 запросов:")
    recent = get_recent_queries(5)
    
    if recent:
        for i, query in enumerate(recent, 1):
            print(f"{i}. '{query['query']}' - {query['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Тип: {query['search_type']}, Результатов: {query['results_count']}")
    else:
        print("   Нет данных о последних запросах")
    
    print("="*60)
    input("\nНажмите Enter для продолжения...")

def show_exit_message():
    """Display exit message."""
    print("\nЗакрытие соединения с базой данных...")
    print("До свидания!")

def ask_continue():
    """Ask user if they want to continue with more results."""
    choice = input("\nПоказать больше результатов? (y/n): ").strip().lower()
    return choice in ['y', 'yes', 'да', 'д']
