from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import SOURCE_DB_URL, DW_DB_URL

class Database:
    def __init__(self, is_source=True):
        """Initialize database connection.
        
        Args:
            is_source (bool): If True, connect to source database, else connect to data warehouse.
        """
        db_url = SOURCE_DB_URL if is_source else DW_DB_URL
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new session."""
        return self.Session()

    def close_session(self, session):
        """Close the given session."""
        if session:
            session.close()
            
    def execute_query(self, query, params=None):
        """Execute a raw SQL query.
        
        Args:
            query (str): SQL query to execute
            params (dict, optional): Parameters for the query
            
        Returns:
            Result of the query execution
        """
        with self.engine.connect() as connection:
            if params:
                result = connection.execute(query, params)
            else:
                result = connection.execute(query)
            return result
            
    def get_engine(self):
        """Get the SQLAlchemy engine."""
        return self.engine