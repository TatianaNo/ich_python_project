import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    Provides access to MongoDB and MySQL configuration for the project.
    """

    # MongoDB settings (for logs and statistics)
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "film_logs")
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

    # MySQL settings (for films data)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME", "films_database")
    MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

    @classmethod
    def get_mongo_connection_string(cls):
        """
        Build a MongoDB connection string based on current settings with proper URL encoding.
        Supports both regular MongoDB and MongoDB Atlas (SRV) connections.

        Returns:
            str: MongoDB connection URI.
        """
        if cls.MONGO_USERNAME and cls.MONGO_PASSWORD:
            username = quote_plus(cls.MONGO_USERNAME)
            password = quote_plus(cls.MONGO_PASSWORD)
            return f"mongodb+srv://{username}:{password}@{cls.MONGO_HOST}/"
        else:
            return f"mongodb+srv://{cls.MONGO_HOST}/"

    @classmethod
    def get_mongo_config(cls):
        """
        Get MongoDB connection configuration as a dictionary.

        Returns:
            dict: MongoDB connection parameters (uri, host, port, database, username, password).
        """
        return {
            "uri": cls.get_mongo_connection_string(),
            "host": cls.MONGO_HOST,
            "port": cls.MONGO_PORT,
            "database": cls.MONGO_DB_NAME,
            "username": cls.MONGO_USERNAME,
            "password": cls.MONGO_PASSWORD,
        }

    @classmethod
    def get_mysql_config(cls):
        """
        Get MySQL connection configuration as a dictionary.

        Returns:
            dict: MySQL connection parameters (host, port, user, password, database, charset, autocommit).
        """
        config = {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USERNAME,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DB_NAME,
            "charset": "utf8mb4",
            "autocommit": True,
        }
        return config


# Create settings instance
settings = Settings()
