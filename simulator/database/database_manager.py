import sqlalchemy
from sqlalchemy.orm import sessionmaker

from simulator.database.models import Base, Pallet, RefillOrder, OpmOrder
import os

# Create the SQLAlchemy URL to point in 'data' directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, "simulation_data.db")
db_url = f"sqlite:///{db_path}"

class DatabaseManager:
    """
    Manages the database connection, session, and provides an API for database operations.
    """
    def __init__(self, db_url: str = db_url):
        self.engine = sqlalchemy.create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def setup_database(self, fresh_start: bool = True):
        """Creates all tables. If fresh_start, it drops all existing tables first."""
        if fresh_start:
            print("INFO: Dropping all tables for a fresh start.")
            Base.metadata.drop_all(self.engine)

        Base.metadata.create_all(self.engine)
        print("INFO: Database tables created successfully.")

    # -----------------
    # Pallet operations
    # -----------------

    def insert_pallet(self, pallet_id: int, location: str, sim_time: float):
        """Insert a new pallet record into the database upon its creation"""
        with self.Session() as session:
            if session.get(Pallet, pallet_id):
                return

            new_pallet = Pallet(
                id=pallet_id,
                location=location,
                destination=None,
                order_id=None,
                last_updated_sim_time=sim_time
            )
            session.add(new_pallet)
            session.commit()


    def update_pallet(self, pallet_id: str, sim_time: float, **kwargs):
        """
        A generic method to update any combination of pallet attributes.
        """
        with self.Session() as session:
            pallet = session.get(Pallet, pallet_id)
            if not pallet:
                print(f"DATABASE-ERROR: Cannot update non-existent pallet '{pallet_id}'.")
                return

            # Dynamically update attributes from keyword arguments
            for key, value in kwargs.items():
                if hasattr(pallet, key):
                    setattr(pallet, key, value)
                else:
                    print(f"DATABASE-WARN: Ignoring unknown attribute '{key}' for Pallet update.")

            # Update sim time
            pallet.last_updated_sim_time = sim_time
            session.commit()

    # ----------------
    # Order operations
    # ----------------

    def insert_refill_order(self, order_id: int, order_time: float, item_id: int, qty: int):
        """Insert a refill order record into the database upon its creation."""
        with self.Session() as session:
            if session.get(RefillOrder, order_id):
                return

            refill_order = RefillOrder(
                order_id=order_id,
                order_time=order_time,
                item_id=item_id,
                qty=qty
            )
            session.add(refill_order)
            session.commit()
