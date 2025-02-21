# app/db/base.py

from app.db.base_class import Base
from app.db.db_engine import engine
from app.models.user import User
from app.models.log import Log
from app.models.mail_log import MailLog
from app.models.process_data import ProcessData
from app.db.db_engine import get_db_engine

engine = get_db_engine()
def create_tables():
    # Create tables for all models linked to Base
    Base.metadata.create_all(bind=engine)

# create_tables()