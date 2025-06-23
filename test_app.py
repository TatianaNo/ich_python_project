#!/usr/bin/env python3
"""
Test script for the film search application
"""

# Test imports
try:
    from ui import show_menu, get_search_keyword, display_films
    from db import initialize_mysql, initialize_mongo, log_search_query
    from settings import settings
    print("✅ Все импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    exit(1)

# Test settings
print("\n📋 Настройки:")
print(f"MongoDB: {settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB_NAME}")
print(f"MySQL: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB_NAME}")

# Test MongoDB connection
print("\n🔍 Тестирование подключения MongoDB...")
try:
    mongo_db = initialize_mongo()
    print("✅ MongoDB подключение успешно")
    
    # Test logging
    log_search_query("test_query", "keyword", 0)
    print("✅ Логирование запросов работает")
    
except Exception as e:
    print(f"❌ Ошибка MongoDB: {e}")

# Test MySQL connection
print("\n🔍 Тестирование подключения MySQL...")
try:
    mysql_conn = initialize_mysql()
    print("✅ MySQL подключение успешно")
    
    # Test basic query
    cursor = mysql_conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    cursor.close()
    print("✅ MySQL запросы работают")
    
except Exception as e:
    print(f"❌ Ошибка MySQL: {e}")
    print("💡 Убедитесь что MySQL сервер запущен и настройки в .env правильные")

# Test UI functions
print("\n🎨 Тестирование UI функций...")
try:
    # Test display with empty data
    display_films([])
    print("✅ UI функции работают")
except Exception as e:
    print(f"❌ Ошибка UI: {e}")

print("\n🎉 Тестирование завершено!")
print("\nДля полного тестирования:")
print("1. Убедитесь что MongoDB запущен")
print("2. Убедитесь что MySQL запущен") 
print("3. Настройте .env файл с правильными параметрами")
print("4. Создайте таблицу 'films' в MySQL")
print("5. Запустите: python main.py")
