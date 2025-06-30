import pymysql
from pymongo import MongoClient
from settings import settings
from functools import lru_cache
import logging
import re

logger = logging.getLogger(__name__)

def check_mongo_availability():
    """
    Check if MongoDB is available and working.
    Returns True if the connection is successful, otherwise False.
    Caches the result for faster repeated checks.
    Prints a warning and enables file logging if MongoDB is unavailable.
    """
    try:
        mongo_config = settings.get_mongo_config()
        client = MongoClient(mongo_config["uri"], serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # Test connection
        logger.info("MongoDB is available")
        return True
    except Exception as e:
        logger.error(f"⚠ MongoDB unavailable: {e}")
        return False


@lru_cache(maxsize=1)
def get_mongo_client():
    connection_string = settings.get_mongo_connection_string()
    # находим между ":" и "@" и заменяем на "***@"
    safe_uri = re.sub(r":[^:@]+@", ":***@", connection_string)  
    logger.info(f"Connecting to MongoDB at {safe_uri}")
    return MongoClient(connection_string)


def initialize_mongo():
    """
    Initialize a MongoDB connection for logs and statistics with caching.
    Returns a MongoDB database object.
    Reuses the connection if it is already open and alive.
    """
    client = get_mongo_client()
    db = client[settings.MONGO_DB_NAME]
    try:
        client.admin.command("ping")
        logger.info("MongoDB connection successful")
        return db
    except Exception:
        logger.warning("MongoDB connection failed, reinitializing...")
        get_mongo_client.cache_clear()
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        return db


@lru_cache(maxsize=1)
def get_mysql_connection():
    config = settings.get_mysql_config()
    return pymysql.connect(**config)


def initialize_mysql():
    """
    Initialize a MySQL connection for films data with caching.
    Returns a MySQL connection object.
    Reuses the connection if it is already open and alive.
    """
    conn = get_mysql_connection()
    try:
        conn.ping(reconnect=True)
        logger.info("MySQL connection successful")
        return conn
    except Exception:
        get_mysql_connection.cache_clear()
        conn = get_mysql_connection()
        logger.warning("Reinitialized MySQL connection")
        return conn


def close_all_connections():
    """
    Close all database connections (MongoDB and MySQL) and clear the cache.
    Use this for proper application shutdown.
    """
    # Close MongoDB connection
    try:
        client = get_mongo_client()
        client.close()
        logger.info("MongoDB connection closed")
    except Exception:
        logger.error("Failed to close MongoDB connection")
        pass
    get_mongo_client.cache_clear()

    # Close MySQL connection
    try:
        conn = get_mysql_connection()
        conn.close()
        logger.info("MySQL connection closed")
    except Exception:
        logger.error("Failed to close MySQL connection")
        pass
    get_mysql_connection.cache_clear()


# Alias for backward compatibility
close_db_connection = close_all_connections
