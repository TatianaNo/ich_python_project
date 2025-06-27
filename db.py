import pandas as pd
import pymysql
from pymongo import MongoClient
from settings import settings

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Global variables for connection caching
_mongo_client = None
_mongo_db = None
_mysql_connection = None
_sqlalchemy_engine: Engine = None
_mongo_available = None

def check_mongo_availability():
    """
    Check if MongoDB is available and working.
    """
    global _mongo_available
    if _mongo_available is not None:
        return _mongo_available
    
    try:
        mongo_config = settings.get_mongo_config()
        client = MongoClient(mongo_config['uri'], serverSelectionTimeoutMS=3000)
        # Try to ping the server
        client.admin.command('ping')
        _mongo_available = True
        return True
    except Exception as e:
        _mongo_available = False
        print(f"⚠ MongoDB недоступен: {e}")
        print("   Логирование будет производиться в локальный файл")
        return False

def initialize_mongo():
    """
    Initialize MongoDB connection for logs and statistics with caching.
    """
    global _mongo_client, _mongo_db
    
    # Return cached connection if exists
    if _mongo_client is not None and _mongo_db is not None:
        try:
            # Test connection to make sure it's still alive
            _mongo_client.admin.command('ping')
            return _mongo_db
        except Exception:
            # Connection is dead, reset cache
            _mongo_client = None
            _mongo_db = None
    
    # Create new connection
    connection_string = settings.get_mongo_connection_string()
    _mongo_client = MongoClient(connection_string)
    _mongo_db = _mongo_client[settings.MONGO_DB_NAME]
    
    return _mongo_db

def initialize_mysql():
    """
    Initialize MySQL connection for films data with caching.
    """
    global _mysql_connection
    
    # Return cached connection if exists and is alive
    if _mysql_connection is not None:
        try:
            _mysql_connection.ping(reconnect=True)
            return _mysql_connection
        except Exception:
            _mysql_connection = None
    
    # Create new connection
    config = settings.get_mysql_config()
    _mysql_connection = pymysql.connect(**config)
    
    return _mysql_connection

def initialize_mysql_engine() -> Engine:
    """
    Инициализация SQLAlchemy Engine для использования с Pandas.
    Автоматически пересоздаёт engine при обрыве соединения.
    """
    global _sqlalchemy_engine

    if _sqlalchemy_engine is not None:
        try:
            # Проверка живости соединения
            conn = _sqlalchemy_engine.connect()
            conn.close()
            return _sqlalchemy_engine
        except Exception:
            _sqlalchemy_engine = None  # Обновим

    # Конфигурация
    config = settings.get_mysql_config()
    user = config['user']
    password = config['password']
    host = config['host']
    port = config['port']
    database = config['database']

    # Строка подключения
    connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    # Создание engine
    _sqlalchemy_engine = create_engine(connection_url, pool_pre_ping=True)
    return _sqlalchemy_engine

def close_all_connections():
    """
    Close all database connections and clear cache.
    """
    global _mongo_client, _mongo_db, _mysql_connection
    
    # Close MongoDB connection
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
    
    # Close MySQL connection
    if _mysql_connection:
        _mysql_connection.close()
        _mysql_connection = None


# Alias for backward compatibility
close_db_connection = close_all_connections

