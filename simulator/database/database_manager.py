import sqlalchemy
from sqlalchemy.orm import sessionmaker
from simulator.database.models import Base, Pallet, RefillOrder, OpmOrder, Item
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

    # ---------------
    # Item operations
    # ---------------

    def insert_item(self, item_id: int, name: str, weight: float, category: str, volume: float, stackable: bool):
        """Insert a new item record"""
        with self.Session() as session:
            if session.get(Item, item_id):
                return

            new_item = Item(
                item_id=item_id,
                name=name,
                weight=weight,
                category=category,
                volume=volume,
                stackable=stackable
            )
            session.add(new_item)
            session.commit()

    # -----------------
    # Pallet operations
    # -----------------

    def insert_pallet(self, pallet_id: int, location: str, sim_time: float):
        """Insert a new pallet record into the database upon its creation"""
        with self.Session() as session:
            if session.get(Pallet, pallet_id):
                return

            new_pallet = Pallet(
                pallet_id=pallet_id,
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

    def insert_opm_order(self, order_id: int, order_time: float, items: dict[int,int]):
        """
        Insert an opm order record.
        The 'items' proxy on OpmOrder knows how to handle the dict as it is.
        """
        with self.Session() as session:
            if session.get(OpmOrder, order_id):
                return

            opm_order = OpmOrder(
                order_id=order_id,
                order_time=order_time,
                items=items
            )
            session.add(opm_order)
            session.commit()