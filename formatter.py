# Output formatting functions - only formatting, no business logic

import os  # for clearing the screen
import textwrap  # for wrapping text in table cells
from tabulate import tabulate  # for formatting tables

def format_table(data, headers=None, align='left'):
    """
    Format a list of dictionaries as a table for console output.
    Wraps long text in cells for better readability.

    Args:
        data (list): List of dictionaries (rows).
        headers (list, optional): List of column headers.
        align (str, optional): Alignment for table cells.

    Returns:
        str: Formatted table as a string.
    """
    table_data = []
    for row in data:
        formatted_row = [
            '\n'.join(textwrap.wrap(' '.join(str(value).split()), 
                                    width=50)) 
                                    if isinstance(value, str) 
                                    else value
            for value in row.values()
        ]
        table_data.append(formatted_row)

    return tabulate(table_data, headers=headers, tablefmt="grid", 
                    stralign="left")

def clear_screen():
    """
    Clear the terminal screen (cross-platform).
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def format_title(text, width=50):
    """
    Format a title with decorative borders.

    Args:
        text (str): Title text.
        width (int): Width of the border.

    Returns:
        str: Formatted title string.
    """
    border = "=" * width
    return f"\n{border}\n{text.center(width)}\n{border}"

def format_menu_option(number, text):
    """
    Format a menu option for display.

    Args:
        number (str|int): Menu item number.
        text (str): Menu item description.

    Returns:
        str: Formatted menu option.
    """
    return f"  {number}. {text}"

def format_section_header(text):
    """
    Format a section header for display.

    Args:
        text (str): Section header text.

    Returns:
        str: Formatted section header.
    """
    return f"\n{text}:"

def format_border(width=50):
    """
    Format a decorative border line.

    Args:
        width (int): Border width.

    Returns:
        str: Border string.
    """
    return "="*width

def format_error(message):
    """
    Format an error message for display.

    Args:
        message (str): Error message text.

    Returns:
        str: Formatted error message.
    """
    return f"ОШИБКА: {message}"

def format_info(message):
    """
    Format an info message for display.

    Args:
        message (str): Info message text.

    Returns:
        str: Formatted info message.
    """
    return f"ИНФО: {message}"

def format_warning(message):
    """
    Format a warning message for display.

    Args:
        message (str): Warning message text.

    Returns:
        str: Formatted warning message.
    """
    return f"ПРЕДУПРЕЖДЕНИЕ: {message}"

def format_prompt(text):
    """
    Format a user input prompt.

    Args:
        text (str): Prompt text.

    Returns:
        str: Formatted prompt.
    """
    return f"{text} "

def format_wait_prompt():
    """
    Format a prompt to wait for user input.

    Returns:
        str: Wait prompt string.
    """
    return "\n Нажмите Enter для продолжения..."


def format_pagination_info(current_page: int, total_results: int, results_per_page: int = 10):
    """
    Format pagination information for display.

    Args:
        current_page (int): Current page number.
        total_results (int): Total number of results.
        results_per_page (int): Number of results per page.

    Returns:
        str: Pagination info string.
    """
    start_item = (current_page - 1) * results_per_page + 1
    end_item = min(current_page * results_per_page, total_results)
    total_pages = (total_results + results_per_page - 1) // results_per_page

    if total_results == 0:
        return format_info("Результатов не найдено")

    return f"Показаны результаты {start_item}-{end_item} из {total_results} (страница {current_page} из {total_pages})"

def format_pagination_prompt():
    """
    Format a prompt for pagination continuation.

    Returns:
        str: Pagination prompt string.
    """
    return format_prompt("Показать следующие 10 результатов? (y/n):")


