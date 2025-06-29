# Output formatting functions - only formatting, no business logic

import os # for clearing the screen
# перенос строк для длинных текстов
# Используем textwrap для автоматического переноса длинных строк в таблицах
import textwrap # for wrapping text in table cells

from tabulate import tabulate # for formatting tables

def format_table(data, headers=None, align='left'):

    table_data = []
    for row in data:
        formatted_row = [
            '\n'.join(textwrap.wrap(' '.join(str(value).split()), width=50)) if isinstance(value, str) else value
            for value in row.values()
        ]
        table_data.append(formatted_row)

    return tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")


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

def format_border(width=50):
    """Format a decorative border."""
    return "="*width

def format_error(message):
    """Format error message."""
    return f"ОШИБКА: {message}"

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
    return "\n Нажмите Enter для продолжения..."


def format_pagination_info(current_page :int, total_results: int, results_per_page : int=10):
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


