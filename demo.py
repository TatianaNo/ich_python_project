#!/usr/bin/env python3
"""
Демонстрационный скрипт для проверки всех функций проекта
"""

from db import (
    initialize_mongo, initialize_mysql, 
    log_search_query, get_popular_queries, get_recent_queries,
    find_films_by_keyword, find_films_by_criteria,
    get_all_genres, get_year_range,
    close_all_connections
)
from ui import display_films, display_popular_queries
import time

def demo_mongo_functions():
    """Демонстрация функций MongoDB (логи и статистика)"""
    print("\n" + "="*60)
    print("🍃 ДЕМОНСТРАЦИЯ ФУНКЦИЙ MONGODB")
    print("="*60)
    
    try:
        # Инициализация MongoDB
        mongo_db = initialize_mongo()
        print("✅ MongoDB подключение успешно")
        
        # Добавляем тестовые логи
        print("\n📝 Добавляем тестовые логи...")
        log_search_query("терминатор", "keyword", 5)
        log_search_query("комедия", "genre_year", 12)
        log_search_query("матрица", "keyword", 3)
        log_search_query("фантастика", "genre_year", 8)
        print("✅ Тестовые логи добавлены")
        
        # Показываем популярные запросы
        print("\n🔥 Популярные запросы:")
        popular = get_popular_queries(3)
        for i, query in enumerate(popular, 1):
            print(f"{i}. '{query['_id']}' - {query['count']} раз(а)")
        
        # Показываем последние запросы
        print("\n⏰ Последние запросы:")
        recent = get_recent_queries(3)
        for i, query in enumerate(recent, 1):
            print(f"{i}. '{query['query']}' - {query['timestamp'].strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"❌ Ошибка MongoDB: {e}")

def demo_mysql_functions():
    """Демонстрация функций MySQL (поиск фильмов)"""
    print("\n" + "="*60)
    print("🐬 ДЕМОНСТРАЦИЯ ФУНКЦИЙ MYSQL")
    print("="*60)
    
    try:
        # Инициализация MySQL
        mysql_conn = initialize_mysql()
        print("✅ MySQL подключение успешно")
        
        # Тестируем поиск по ключевому слову
        print("\n🔍 Поиск по ключевому слову 'test':")
        films = find_films_by_keyword("test", limit=3)
        if films:
            display_films(films)
        else:
            print("   Фильмы не найдены (это нормально, если таблица пуста)")
        
        # Тестируем поиск по критериям
        print("\n🎭 Поиск по жанру 'драма':")
        films = find_films_by_criteria(genre="драма", limit=3)
        if films:
            display_films(films)
        else:
            print("   Фильмы не найдены (это нормально, если таблица пуста)")
        
        # Получаем все жанры
        print("\n🎪 Все жанры в базе:")
        genres = get_all_genres()
        if genres:
            print(f"   Найдено жанров: {len(genres)}")
            print(f"   Примеры: {', '.join(genres[:5])}")
        else:
            print("   Жанры не найдены (это нормально, если таблица пуста)")
        
        # Получаем диапазон лет
        print("\n📅 Диапазон лет:")
        year_range = get_year_range()
        if year_range['min_year'] and year_range['max_year']:
            print(f"   От {year_range['min_year']} до {year_range['max_year']}")
        else:
            print("   Данные о годах не найдены (это нормально, если таблица пуста)")
            
    except Exception as e:
        print(f"❌ Ошибка MySQL: {e}")
        print("   💡 Убедитесь, что:")
        print("   - MySQL сервер запущен")
        print("   - База данных существует")
        print("   - Настройки в .env файле корректны")

def demo_ui_functions():
    """Демонстрация UI функций"""
    print("\n" + "="*60)
    print("🖥️  ДЕМОНСТРАЦИЯ UI ФУНКЦИЙ")
    print("="*60)
    
    # Показываем статистику (если есть данные)
    try:
        display_popular_queries()
    except Exception as e:
        print(f"❌ Ошибка UI: {e}")

def main():
    """Главная функция демонстрации"""
    print("🚀 ДЕМОНСТРАЦИЯ ПРОЕКТА ПОИСКА ФИЛЬМОВ")
    print("="*60)
    
    # Демонстрация MongoDB
    demo_mongo_functions()
    
    # Пауза
    time.sleep(1)
    
    # Демонстрация MySQL  
    demo_mysql_functions()
    
    # Пауза
    time.sleep(1)
    
    # Демонстрация UI
    demo_ui_functions()
    
    # Закрываем соединения
    print("\n" + "="*60)
    print("🔄 Закрытие соединений...")
    close_all_connections()
    print("✅ Все соединения закрыты")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("="*60)

if __name__ == "__main__":
    main()
