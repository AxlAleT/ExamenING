from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_engine(db_url):
    return create_engine(db_url)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()