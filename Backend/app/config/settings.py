import os
from dotenv import load_dotenv
from app.core.config import config

load_dotenv()


class Config:
    """Dynamic settings configuration from environment variables and .env file."""

    # MSSQL and SQLite Configurations
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_URL = os.getenv("DB_URL", "sqlite:///database.db")
    # DB_TYPE = os.getenv("DB_TYPE")
    DB_HOST = os.getenv("CONNECTION_STRING_SERVER")
    DB_NAME = os.getenv("DATABASE_NAME")
    DB_DRIVER = os.getenv("DB_DRIVER", "{SQL Server}")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
    DB_TIMEOUT = os.getenv("DB_TIMEOUT", "60")

    # Logging Configuration
    # LOG_DIR = os.path.join('.', 'logs', 'error_logs')
    # os.makedirs(LOG_DIR, exist_ok=True)

    # SMTP Configuration for Email
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    # LDAP Configuration
    LDAP_SERVER_URL = config.LDAP_SERVER_URL
    LDAP_PORT = config.LDAP_PORT
    LDAP_BIND_DN = config.LDAP_BIND_DN
    LDAP_BIND_PASSWORD = config.LDAP_BIND_PASSWORD
    LDAP_BASE_DN = config.LDAP_BASE_DN
    LDAP_USER_SEARCH_FILTER = config.LDAP_USER_SEARCH_FILTER
    LDAP_USER_ATTRIBUTES = config.LDAP_USER_ATTRIBUTES



config = Config