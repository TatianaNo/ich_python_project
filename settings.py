import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables
    """
    
    # MongoDB settings (for logs and statistics)
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'film_logs')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
    
    # MySQL settings (for films data)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DB_NAME = os.getenv('MYSQL_DB_NAME', 'films_database')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    @classmethod
    def get_mongo_connection_string(cls):
        """
        Build MongoDB connection string based on settings
        """
        if cls.MONGO_USERNAME and cls.MONGO_PASSWORD:
            return f'mongodb://{cls.MONGO_USERNAME}:{cls.MONGO_PASSWORD}@{cls.MONGO_HOST}:{cls.MONGO_PORT}/'
        else:
            return f'mongodb://{cls.MONGO_HOST}:{cls.MONGO_PORT}/'
    
    @classmethod
    def get_mysql_config(cls):
        """
        Get MySQL connection configuration
        """
        config = {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'user': cls.MYSQL_USERNAME,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        return config

# Create settings instance
settings = Settings()