import sqlalchemy
from sqlalchemy.orm import sessionmaker
from simulator.database.models import Base, Pallet, Order, RefillOrder, OpmOrder, Item, OrderStatus
from simulator.core.utils.logging_config import log_manager
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
                id=item_id,
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

    def insert_pallet(self, pallet_id: int, location: str, destination: str | None,
                      order_id: int | None, sim_time: float):
        """Insert a new pallet record into the database upon its creation"""
        with self.Session() as session:
            if session.get(Pallet, pallet_id):
                return

            new_pallet = Pallet(
                id=pallet_id,
                location=location,
                destination=destination,
                order_id=order_id,
                last_updated_sim_time=sim_time
            )
            session.add(new_pallet)
            session.commit()


    def update_pallet(self, pallet_id: int, sim_time: float, **kwargs):
        """
        A generic method to update any combination of pallet attributes.
        """
        with self.Session() as session:
            pallet = session.get(Pallet, pallet_id)
            if not pallet:
                return

            # Dynamically update attributes from keyword arguments
            for key, value in kwargs.items():
                if hasattr(pallet, key):
                    setattr(pallet, key, value)

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
                id=order_id,
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
                id=order_id,
                order_time=order_time,
                items=items
            )
            session.add(opm_order)
            session.commit()

    def update_order(self, order_id: int, **kwargs):
        """
        A generic method to update any combination of order attributes.
        """
        with self.Session() as session:
            order = session.get(Order, order_id)
            if not order:
                return

            # Dynamically update attributes from keyword arguments
            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            session.commit()

    def query_orders(self, **kwargs) -> list[Order]:
        """
        A flexible method to query the orders table with dynamic filters.
        """
        with self.Session() as session:
            try:
                # Start with a base query on the polymorphic Order class
                query = session.query(Order)

                # If we need to filter by item_id, we must join with RefillOrder
                if 'item_id' in kwargs:
                    query = query.join(RefillOrder)

                # Separate control args from filter args
                control_args = ['order_by', 'limit']
                filter_kwargs = {k: v for k, v in kwargs.items() if k not in control_args}

                for key, value in filter_kwargs.items():
                    if key == 'min_order_time':
                        query = query.filter(Order.order_time >= value)
                    elif key == 'max_order_time':
                        query = query.filter(Order.order_time <= value)
                    elif key == 'item_id':
                        query = query.filter(RefillOrder.item_id == value)
                    elif hasattr(Order, key):
                        # This handles direct attributes like 'id', 'type', 'status'
                        query = query.filter(getattr(Order, key) == value)
                    else:
                        print(f"Unknown filter key '{key}' ignored in query_orders.")

                # Apply ordering
                if 'order_by' in kwargs:
                    order_by_col = kwargs['order_by']
                    if order_by_col.startswith('-'):
                        # Descending order
                        col_name = order_by_col[1:]
                        if hasattr(Order, col_name):
                            query = query.order_by(sqlalchemy.desc(getattr(Order, col_name)))
                    else:
                        # Ascending order
                        if hasattr(Order, order_by_col):
                            query = query.order_by(getattr(Order, order_by_col))

                # --- Apply Limit ---
                if 'limit' in kwargs:
                    query = query.limit(kwargs['limit'])

                # Execute the final query
                return query.all()

            except Exception as e:
                print("An error occurred during order query.")
                return []