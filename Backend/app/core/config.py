# app/core/config.py

import os
from dotenv import load_dotenv
from pathlib import Path
import yaml
from urllib.parse import quote_plus


load_dotenv()

class Config:
    def __init__(self):
        config_path = Path(__file__).parent.parent / 'resources' / 'config.yml'
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        self.SECRET_KEY = config['SECRET_KEY']
        self.ALGORITHM = config['ALGORITHM']
        self.ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']
        self.DB_DRIVER = config['DATABASE']['DB_DRIVER']
        self.DB_HOST = config['DATABASE']['DB_HOST']
        self.DB_PORT = config['DATABASE']['DB_PORT']
        self.DB_USER = config['DATABASE']['DB_USER']
        self.DB_PASSWORD = config['DATABASE']['DB_PASSWORD']
        self.DB_NAME = config['DATABASE']['DB_NAME']
        self.DB_TRUSTED_CONNECTION = config['DATABASE']['DB_TRUSTED_CONNECTION']
        self.DB_TIMEOUT = config['DATABASE']['DB_TIMEOUT']
        self.FRONTEND_URL = config.get('FRONTEND_URL', 'http://localhost:3000')  # Added FRONTEND_URL
        self.EMAIL_OTP_EXPIRATION_MINUTES = config['EMAIL_OTP_EXPIRATION_MINUTES']
        
        
        # LDAP Configuration
        ldap_config = config['LDAP']
        self.LDAP_SERVER_URL = ldap_config['LDAP_SERVER_URL']
        self.LDAP_PORT = ldap_config['LDAP_PORT']
        self.LDAP_BIND_DN = ldap_config['LDAP_BIND_DN']
        self.LDAP_BIND_PASSWORD = ldap_config['LDAP_BIND_PASSWORD']
        self.LDAP_BASE_DN = ldap_config['LDAP_BASE_DN']
        self.LDAP_USER_SEARCH_FILTER = ldap_config['LDAP_USER_SEARCH_FILTER']
        # Ensure LDAP_USER_ATTRIBUTES is always a list
        self.LDAP_USER_ATTRIBUTES = (
            ldap_config['LDAP_USER_ATTRIBUTES']
            if isinstance(ldap_config['LDAP_USER_ATTRIBUTES'], list)
            else ldap_config['LDAP_USER_ATTRIBUTES'].split(",")
        )

config = Config()

DB_URL = (
    f"mssql+pyodbc://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST},{config.DB_PORT}/{config.DB_NAME}"
    f"?driver=SQL+Server&TrustServerCertificate=yes&MARS_Connection=Yes&timeout={config.DB_TIMEOUT}"
)

# connection_str = (
#     f"DRIVER={{{config.DB_DRIVER}}};"
#     f"SERVER={config.DB_HOST},{config.DB_PORT};"
#     f"DATABASE={config.DB_NAME};"
#     f"UID={config.DB_USER};"
#     f"PWD={config.DB_PASSWORD};"
#     f"TrustServerCertificate={config.DB_TRUSTED_CONNECTION};"
#     f"Connection Timeout={config.DB_TIMEOUT};"
# )


# DB_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_str)}"
