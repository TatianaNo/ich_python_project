# Output formatting functions - only formatting, no business logic
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_title(text, width=50):
    """Format a title with decorative borders."""
    border = "=" * width
    return f"\n{border}\n{text.center(width)}\n{border}"

def format_menu_option(number, text):
    """Format a menu option."""
    return f"  {number}. {text}"

def format_section_header(text):
    """Format a section header."""
    return f"\n{text}:"

def format_film_title(index, title, year=None):
    """Format a film title with index."""
    if year and year != "Не указан":
        return f"\n{index}. {title} ({year})"
    else:
        return f"\n{index}. {title}"

def format_film_detail(label, value):
    """Format a film detail line."""
    if value and value != "Не указан" and value != "Нет описания":
        return f"   {label}: {value}"
    return None  # Don't display if no value

def format_query_item(index, query_text, count=None, timestamp=None):
    """Format a query item for statistics."""
    if count is not None:
        return f"{index}. '{query_text}' - {count} раз(а)"
    elif timestamp is not None:
        return f"{index}. '{query_text}' - {timestamp}"
    else:
        return f"{index}. '{query_text}'"

def format_query_detail(label, value):
    """Format query detail line for statistics."""
    return f"   {label}: {value}"

def format_border(width=60):
    """Format a decorative border."""
    return "="*width

def format_error(message):
    """Format error message."""
    return f"ОШИБКА: {message}"

def format_success(message):
    """Format success message."""
    return f"УСПЕХ: {message}"

def format_info(message):
    """Format info message."""
    return f"ИНФО: {message}"

def format_warning(message):
    """Format warning message."""
    return f"ПРЕДУПРЕЖДЕНИЕ: {message}"

def format_prompt(text):
    """Format a user input prompt."""
    return f"{text} "

def format_wait_prompt():
    """Format wait for user prompt."""
    return "\nНажмите Enter для продолжения..."

def format_films_list(films):
    """Format a complete list of films for display."""
    if not films:
        return [format_error("Фильмы не найдены.")]
    
    result = []
    
    for i, film in enumerate(films, 1):
        title = film.get('title', 'Без названия')
        year = film.get('release_year', film.get('year'))
        genre = film.get('genre')
        rating = film.get('rating')
        description = film.get('description')
        
        result.append(format_film_title(i, title, year))
        
        # Only add details if they have meaningful values
        genre_detail = format_film_detail("Жанр", genre)
        if genre_detail:
            result.append(genre_detail)
            
        rating_detail = format_film_detail("Рейтинг", rating)
        if rating_detail:
            result.append(rating_detail)
            
        if description and description != "Нет описания":
            desc_text = description[:100] + "..." if len(description) > 100 else description
            desc_detail = format_film_detail("Описание", desc_text)
            if desc_detail:
                result.append(desc_detail)
    
    return result

def format_pagination_info(current_page, total_results, results_per_page=10):
    """Format pagination information."""
    start_item = (current_page - 1) * results_per_page + 1
    end_item = min(current_page * results_per_page, total_results)
    total_pages = (total_results + results_per_page - 1) // results_per_page
    
    if total_results == 0:
        return format_info("Результатов не найдено")
    
    return f"Показаны результаты {start_item}-{end_item} из {total_results} (страница {current_page} из {total_pages})"

def format_pagination_prompt():
    """Format pagination continuation prompt."""
    return format_prompt("Показать следующие 10 результатов? (y/n):")

def format_popular_queries_section(popular_queries):
    """Format popular queries section for display."""
    result = [format_section_header("Топ-5 популярных запросов")]
    
    if popular_queries:
        for i, query in enumerate(popular_queries, 1):
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
                
                result.append(format_query_item(i, query_text, count=count))
                if search_type != 'unknown':
                    result.append(format_query_detail("Тип", f"{search_type}, Последний поиск: {last_searched_str}"))
                else:
                    result.append(format_query_detail("Количество запросов", count))
    else:
        result.append(format_error("   Нет данных о популярных запросах"))
    
    return result

def format_recent_queries_section(recent_queries):
    """Format recent queries section for display."""
    result = [format_section_header("Последние 5 запросов")]
    
    if recent_queries:
        for i, query in enumerate(recent_queries, 1):
            query_text = query.get('query', 'unknown')
            search_type = query.get('search_type', 'unknown')
            results_count = query.get('results_count', 0)
            timestamp = query.get('timestamp', 'unknown')
            
            # Handle timestamp formatting
            if hasattr(timestamp, 'strftime'):
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                timestamp_str = str(timestamp)
            
            result.append(format_query_item(i, query_text, timestamp=timestamp_str))
            result.append(format_query_detail("Тип", f"{search_type}, Результатов: {results_count}"))
    else:
        result.append(format_error("   Нет данных о последних запросах"))
    
    return result

def format_general_stats_section(stats):
    """Format general statistics section for display."""
    result = []
    if stats and stats['total_searches'] > 0:
        result.append(format_section_header("Общая статистика"))
        result.append(f"   Всего поисков: {stats['total_searches']}")
        if stats['search_types']:
            result.append("   По типам:")
            for search_type, count in stats['search_types'].items():
                result.append(f"     - {search_type}: {count}")
    return result
