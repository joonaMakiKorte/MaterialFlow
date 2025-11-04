import sqlalchemy
from sqlalchemy.orm import sessionmaker
from simulator.database.models import Base, Pallet

class DatabaseManager:
    """
    Manages the database connection, session, and provides an API for database operations.
    """
    def __init__(self, db_url: str = "sqlite://simulation_data.db"):
        self.engine = sqlalchemy.create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def setup_database(self):
        """Creates all the tables defined in the models."""
        # This will check if the tables exist before creating them.
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully.")