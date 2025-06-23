# Main application entry point
from ui import (
    show_menu, get_menu_choice, get_search_keyword, get_genre_choice, get_year_range_choice,
    display_films, display_popular_queries, show_exit_message, search_films_with_pagination,
    search_films_by_genre_with_pagination, search_films_by_year_range_with_pagination
)
from mysql_connector import close_mysql_connection
from log_writer import close_mongo_connection
from formatter import format_success

def main():
    """Main application loop."""
    while True:
        show_menu()
        choice = get_menu_choice()        
        if choice == "1":
            # Search by keyword with pagination
            print(format_success("Вы выбрали поиск по ключевому слову."))
            keyword = get_search_keyword()
            search_films_with_pagination(keyword)
            
        elif choice == "2":
            # Search by genre
            print(format_success("Вы выбрали поиск по жанру."))
            genre = get_genre_choice()
            if genre:
                search_films_by_genre_with_pagination(genre)
            
        elif choice == "3":
            # Search by year range
            print(format_success("Вы выбрали поиск по диапазону годов."))
            year_params = get_year_range_choice()
            if year_params:
                search_films_by_year_range_with_pagination(year_params)
            
        elif choice == "4":
            # View popular queries
            display_popular_queries()
            
        elif choice == "9":
            # Exit
            break
    
    # Close database connections when exiting
    show_exit_message()
    close_mysql_connection()
    close_mongo_connection()

if __name__ == "__main__":
    main()