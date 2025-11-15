import sqlalchemy
from sqlalchemy.orm import sessionmaker
from simulator.database.models import Base, Pallet, Order, RefillOrder, OpmOrder, Item, OrderStatus
import os
import logging
logger = logging.getLogger(__name__)

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
        try:
            self.engine = sqlalchemy.create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"DatabaseManager initialized with engine for URL: {db_url}")
        except Exception as e:
            logger.critical("Failed to initialize DatabaseManager engine.", exc_info=True)
            raise  # Re-raise the exception to stop the application if the DB can't be set up

    def setup_database(self, fresh_start: bool = True):
        """Creates all tables. If fresh_start, it drops all existing tables first."""
        try:
            if fresh_start:
                logger.info("Dropping all existing database tables.")
                Base.metadata.drop_all(self.engine)

            logger.info("Creating all database tables from models.")
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully.")
        except Exception as e:
            logger.critical("Failed to setup database tables.", exc_info=True)
            raise

    # ---------------
    # Item operations
    # ---------------

    def insert_item(self, item_id: int, name: str, weight: float, category: str, volume: float, stackable: bool):
        """Insert a new item record, rolling back on error."""
        session = self.Session()
        try:
            if session.get(Item, item_id):
                logger.debug(f"Skipping duplicate item insertion for ID {item_id}.")
                return

            new_item = Item(
                id=item_id, name=name, weight=weight,
                category=category, volume=volume, stackable=stackable
            )
            session.add(new_item)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to insert item with ID {item_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def get_all_item_categories(self) -> list[str]:
        """Helper function to get a unique, sorted list of all item categories."""
        with self.Session() as session:
            try:
                categories = session.query(Item.category).distinct().order_by(Item.category).all()
                return [category[0] for category in categories]
            except Exception as e:
                logger.error("Failed to retrieve item categories.", exc_info=True)
                return []

    def query_items(self, **kwargs) -> list[Item]:
        """
        A flexible method to query the items table with dynamic filters.
        """
        with self.Session() as session:
            try:
                query = session.query(Item)

                control_args = ['order_by']
                filter_kwargs = {k: v for k, v in kwargs.items() if k not in control_args}

                for key, value in filter_kwargs.items():
                    if key == 'name_contains':
                        query = query.filter(Item.name.ilike(f"%{value}%"))
                    elif hasattr(Item, key):
                        query = query.filter(getattr(Item, key) == value)
                    else:
                        logger.warning(f"Unknown filter key '{key}' ignored in item query.")

                # Apply Ordering
                if 'order_by' in kwargs:
                    order_by_col = kwargs['order_by']
                    if order_by_col.startswith('-'):
                        col_name = order_by_col[1:]
                        if hasattr(Item, col_name):
                            query = query.order_by(sqlalchemy.desc(getattr(Item, col_name)))
                    else:
                        if hasattr(Item, order_by_col):
                            query = query.order_by(getattr(Item, order_by_col))
                else:
                    query = query.order_by(Item.id)

                results = query.all()
                return results
            except Exception as e:
                logger.error(f"An error occurred during item query with filters {kwargs}.", exc_info=True)
                return []

    # -----------------
    # Pallet operations
    # -----------------

    def insert_pallet(self, pallet_id: int, location: str, sim_time: float):
        """Insert a new pallet record, rolling back on error."""
        session = self.Session()
        try:
            if session.get(Pallet, pallet_id):
                logger.debug(f"Skipping duplicate pallet insertion for ID {pallet_id}.")
                return

            new_pallet = Pallet(
                id=pallet_id, location=location, last_updated_sim_time=sim_time
            )
            session.add(new_pallet)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to insert pallet with ID {pallet_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()


    def update_pallet(self, pallet_id: int, sim_time: float, **kwargs):
        """
        A generic method to update any combination of pallet attributes.
        """
        session = self.Session()
        try:
            pallet = session.get(Pallet, pallet_id)
            if not pallet:
                logger.warning(f"Cannot update non-existent pallet '{pallet_id}'.")
                return

            for key, value in kwargs.items():
                if hasattr(pallet, key):
                    setattr(pallet, key, value)
                else:
                    logger.warning(f"Ignoring unknown attribute '{key}' for Pallet update.")

            pallet.last_updated_sim_time = sim_time
            session.commit()
        except Exception as e:
            logger.error(f"Failed to update pallet with ID {pallet_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def query_pallets(self, **kwargs) -> list[Pallet]:
        """
        A flexible method to query the pallets table with dynamic filters.
        """
        with self.Session() as session:
            try:
                query = session.query(Pallet)

                # Separate control args from filter args
                control_args = ['order_by']
                filter_kwargs = {k: v for k, v in kwargs.items() if k not in control_args}

                # Apply dynamic filters
                for key, value in filter_kwargs.items():
                    if hasattr(Pallet, key):
                        query = query.filter(getattr(Pallet, key) == value)
                    else:
                        logger.warning(f"Unknown filter key '{key}' ignored in pallet query.")

                # Apply ordering
                if 'order_by' in kwargs:
                    order_by_col = kwargs['order_by']
                    if order_by_col.startswith('-'):
                        # Descending order (e.g., '-last_updated_sim_time')
                        col_name = order_by_col[1:]
                        if hasattr(Pallet, col_name):
                            query = query.order_by(sqlalchemy.desc(getattr(Pallet, col_name)))
                    else:
                        # Ascending order
                        if hasattr(Pallet, order_by_col):
                            query = query.order_by(getattr(Pallet, order_by_col))
                else:
                    # Default ordering if not specified
                    query = query.order_by(Pallet.id)

                results = query.all()
                return results
            except Exception as e:
                logger.error(f"An error occurred during pallet query with filters {kwargs}.", exc_info=True)
                return []

    # ----------------
    # Order operations
    # ----------------

    def insert_refill_order(self, order_id: int, order_time: float, item_id: int, qty: int):
        """Insert a refill order record, rolling back on error."""
        session = self.Session()
        try:
            if session.get(RefillOrder, order_id):
                logger.debug(f"Skipping duplicate RefillOrder insertion for ID {order_id}.")
                return

            refill_order = RefillOrder(
                id=order_id, order_time=order_time, item_id=item_id, qty=qty
            )
            session.add(refill_order)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to insert RefillOrder with ID {order_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def insert_opm_order(self, order_id: int, order_time: float, items: dict[int,int]):
        """
        Insert an opm order record.
        The 'items' proxy on OpmOrder knows how to handle the dict as it is.
        """
        session = self.Session()
        try:
            if session.get(OpmOrder, order_id):
                logger.debug(f"Skipping duplicate OpmOrder insertion for ID {order_id}.")
                return

            opm_order = OpmOrder(id=order_id, order_time=order_time, items=items)
            session.add(opm_order)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to insert OpmOrder with ID {order_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def update_order(self, order_id: int, **kwargs):
        """
        A generic method to update any combination of order attributes.
        """
        session = self.Session()
        try:
            order = session.get(Order, order_id)
            if not order:
                logger.warning(f"Cannot update non-existent order '{order_id}'.")
                return

            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)

            session.commit()
        except Exception as e:
            logger.error(f"Failed to update order with ID {order_id}.", exc_info=True)
            session.rollback()
        finally:
            session.close()

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
                control_args = ['order_by']
                filter_kwargs = {k: v for k, v in kwargs.items() if k not in control_args}

                for key, value in filter_kwargs.items():
                    if key == 'min_order_time':
                        query = query.filter(Order.order_time >= value)
                    elif key == 'max_order_time':
                        query = query.filter(Order.order_time <= value)
                    elif hasattr(Order, key):
                        query = query.filter(getattr(Order, key) == value)
                    else:
                        logger.warning(f"Unknown filter key '{key}' ignored in query_orders.")

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

                results = query.all()
                return results
            except Exception as e:
                logger.error(f"An error occurred during order query with filters {kwargs}.", exc_info=True)
                return []