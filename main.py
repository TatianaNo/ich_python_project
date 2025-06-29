# Main application entry point
from ui import (
    show_recent_queries,
    show_menu,
    get_menu_choice,
    display_popular_queries,
    show_exit_message,
    search_film_by_title,
    search_film_by_genre_and_year,
    search_film_by_actor,
)


def main():
    """
    Main application loop.
    Handles user interaction and menu navigation.
    Calls appropriate UI functions based on user choice.
    Loops until the user selects exit.
    """
    while True:
        show_menu()
        choice = get_menu_choice()
        if choice == "1":
            # Search by title
            print("Вы выбрали поиск по названию.")
            search_film_by_title()

        elif choice == "2":
            # Search by genre and year range
            print("Вы выбрали поиск по жанру и диапазону годов.")
            search_film_by_genre_and_year()

        elif choice == "3":
            # Search by actor
            print("Вы выбрали поиск по актеру.")
            search_film_by_actor()

        elif choice == "4":
            # View popular queries
            display_popular_queries()

        elif choice == "5":
            # View recent unique queries
            print("Последние уникальные запросы:")
            show_recent_queries()

        elif choice == "0":
            show_exit_message()
            break

    # Close database connections when exiting
    # (handled in show_exit_message or db module)


if __name__ == "__main__":
    main()
