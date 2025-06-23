from ui import (
    show_menu, get_menu_choice, get_search_keyword, get_genre_and_year_range,
    display_film, display_films, display_popular_queries, show_exit_message,
    BLUE, YELLOW, GREEN, RESET
)
from db import (
    find_films_by_keyword, find_films_by_criteria,
    close_all_connections
)
from settings import settings

def main():
    """Main application loop."""
    while True:
        show_menu()
        choice = get_menu_choice()        
        if choice == "1":
            # Search by keyword
            print(f"{GREEN}Вы выбрали поиск по ключевому слову.{RESET}")
            keyword = get_search_keyword()
            films = find_films_by_keyword(keyword)
            display_films(films)
            
        elif choice == "2":
            # Search by genre and year range
            print(f"{GREEN}Вы выбрали поиск по жанру и диапазону годов.{RESET}")
            criteria = get_genre_and_year_range()
            films = find_films_by_criteria(
                genre=criteria['genre'],
                year_from=criteria['year_from'],
                year_to=criteria['year_to']
            )
            display_films(films)
            
        elif choice == "3":
            # View popular queries
            display_popular_queries()
            
        elif choice == "9":
            # Exit
            break
    
    # Close database connection when exiting
    show_exit_message()
    close_all_connections()

if __name__ == "__main__":
    main()