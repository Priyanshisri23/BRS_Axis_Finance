from sqlalchemy import create_engine
from urllib.parse import quote_plus
from app.config.settings import Config
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_URL

# def create_mssql_connection_string():
#     """
#     Create the connection string for MSSQL based on the environment variables in settings.py.
#     :return: MSSQL connection string for SQLAlchemy.
#     """
#     if Config.DB_USER and Config.DB_PASSWORD:
#         connection_string = (
#             f"mssql+pyodbc://{Config.DB_USER}:{quote_plus(Config.DB_PASSWORD)}@{Config.DB_HOST}/{Config.DB_NAME}"
#             f"?driver={Config.DB_DRIVER}&TrustServerCertificate=yes&Trusted_Connection={Config.DB_TRUSTED_CONNECTION}&Connection Timeout={Config.DB_TIMEOUT}"
#         )
#     else:
#         connection_string = (
#             f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={Config.DB_DRIVER};SERVER={Config.DB_HOST};DATABASE={Config.DB_NAME};Trusted_Connection={Config.DB_TRUSTED_CONNECTION};MARS_Connection=Yes;Connection Timeout={Config.DB_TIMEOUT};')}"
#         )
#     return connection_string


# DATABASE_HOST = '10.0.219.92'
DATABASE_HOST = 'VBINBRSUTDB01'
DB_PORT = '2433'
DATABASE_NAME = "BRSUAT"
DB_USERNAME = 'BRS'
DB_PASSWORD = 'Axis@1234'


# def get_db_engine(db_type="mssql"):
#     if db_type == "mssql":
#         connection_VARCHAR = (f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={{SQL Server}};SERVER={DATABASE_HOST},{DB_PORT};DATABASE={DATABASE_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;Connection Timeout=60;')}")
#         # connection_VARCHAR=""
#         # print("we are working with this connection",connection_VARCHAR)

#         return create_engine(connection_VARCHAR, echo=False, fast_executemany=True)
#     else:
#         return create_engine(db_url, echo=False)
# # print(get_db_engine())

# engine = get_db_engine()

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_session():

#     Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#     return Session


# def get_db() -> Generator:
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()


# New code from BRS project

"""Set up SQLAlchemy engine for both SQLite and MSSQL"""
# def get_db_engine(db_type="sqlite", db_url="sqlite:///database.db"):
def get_db_engine(db_type="mssql", db_url="sqlite:///database.db"):
    if db_type == "mssql":
        connection_VARCHAR = (f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={{SQL Server}};SERVER={DATABASE_HOST},{DB_PORT};DATABASE={DATABASE_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;Connection Timeout=60;')}")
        # connection_VARCHAR=""
        # print("we are working with this connection",connection_VARCHAR)

        return create_engine(connection_VARCHAR, echo=False, fast_executemany=True)
    else:
        return create_engine(db_url, echo=False)
 
engine = get_db_engine()

print(f"Engine: {engine}")
 
"""Set up session for both databases"""
def get_session(engine=engine):
    # Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


SessionLocal = get_session()

print(f"Session Local :{SessionLocal}")