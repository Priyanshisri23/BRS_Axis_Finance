# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from app.core.config import config
from typing import Generator
from app.db.base_class import Base

def get_db_engine():
    driver = quote_plus(config.DB_DRIVER)
    connection_string = (
        f"mssql+pyodbc://{config.DB_USER}:{quote_plus(config.DB_PASSWORD)}@{config.DB_HOST}/{config.DB_NAME}"
        f"?driver={driver}&TrustServerCertificate=yes&MARS_Connection=Yes&timeout={config.DB_TIMEOUT}"
    )
    # print(connection_string)
    engine = create_engine(connection_string, echo=False, fast_executemany=True)
    return engine

# Create engine and session factory

engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
