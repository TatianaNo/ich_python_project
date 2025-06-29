import pymysql
from pymongo import MongoClient
from settings import settings

# Global variables for connection caching
_mongo_client = None
_mongo_db = None
_mysql_connection = None
_mongo_available = None


def check_mongo_availability():
    """
    Check if MongoDB is available and working.
    Returns True if the connection is successful, otherwise False.
    Caches the result for faster repeated checks.
    Prints a warning and enables file logging if MongoDB is unavailable.
    """
    global _mongo_available
    if _mongo_available is not None:
        return _mongo_available
    try:
        mongo_config = settings.get_mongo_config()
        client = MongoClient(mongo_config["uri"], serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # Test connection
        _mongo_available = True
        return True
    except Exception as e:
        _mongo_available = False
        print(f"⚠ MongoDB unavailable: {e}")
        print("   Logging will be performed to a local file")
        return False


def initialize_mongo():
    """
    Initialize a MongoDB connection for logs and statistics with caching.
    Returns a MongoDB database object.
    Reuses the connection if it is already open and alive.
    """
    global _mongo_client, _mongo_db

    # Return cached connection if exists
    if _mongo_client is not None and _mongo_db is not None:
        try:
            _mongo_client.admin.command("ping")
            return _mongo_db
        except Exception:
            _mongo_client = None
            _mongo_db = None

    # Create new connection
    connection_string = settings.get_mongo_connection_string()
    _mongo_client = MongoClient(connection_string)
    _mongo_db = _mongo_client[settings.MONGO_DB_NAME]

    return _mongo_db


def initialize_mysql():
    """
    Initialize a MySQL connection for films data with caching.
    Returns a MySQL connection object.
    Reuses the connection if it is already open and alive.
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


def close_all_connections():
    """
    Close all database connections (MongoDB and MySQL) and clear the cache.
    Use this for proper application shutdown.
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
