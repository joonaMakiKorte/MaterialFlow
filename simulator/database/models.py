import enum
import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from typing import List, Dict


class Base(DeclarativeBase):
    """Base class all models inherit from"""
    pass


class Item(Base):
    """
    Represents an item in the factory catalogue. Maps to the 'items' table.
    This table holds the master data for all stock keeping units.
    """
    __tablename__ = 'items'

    item_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(100), unique=True, nullable=False)
    weight: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=False)
    category: Mapped[str] = mapped_column(sqlalchemy.String(50), nullable=False)
    volume: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=False)
    stackable: Mapped[bool] = mapped_column(sqlalchemy.Boolean, nullable=False)


class OrderStatus(enum.Enum):
    """Enumeration of possible order states."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """
    SQLAlchemy model for the base 'orders' table.
    """
    __tablename__ = 'orders'

    # Columns common to all orders
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sqlalchemy.String) # Discriminator column
    order_time: Mapped[float] = mapped_column(sqlalchemy.Float)
    status: Mapped[OrderStatus] = mapped_column(sqlalchemy.Enum(OrderStatus), default=OrderStatus.PENDING)


    # Inheritance Settings
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'order',
    }


class RefillOrder(Order):
    """
    SQLAlchemy model for the 'refill_orders' table.
    Inherits from the Order model.
    """
    __tablename__ = 'refill_orders'

    id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.item_id'), nullable=False)
    qty: Mapped[int] = mapped_column(sqlalchemy.Integer)

    # Relationship to the Item object
    item: Mapped['Item'] = relationship(lazy="joined")

    __mapper_args__ = {'polymorphic_identity': 'RefillOrder'}


class OpmOrderItem(Base):
    """Stores the key-value pairs from the OpmOrder.items dictionary."""
    __tablename__ = 'opm_order_items'
    opm_order_id: Mapped[int] = mapped_column(ForeignKey('opm_orders.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.item_id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(sqlalchemy.Integer)

    # Relationship to the Item object
    item: Mapped['Item'] = relationship(lazy="joined")


class OpmOrder(Order):
    """
    SQLAlchemy model for the 'opm_orders' table.
    Inherits from the Order model.
    """
    __tablename__ = 'opm_orders'


    id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    _items_assoc: Mapped[List[OpmOrderItem]] = relationship(
        cascade="all, delete-orphan"
    )
    items: Dict[int, int] = association_proxy(
        '_items_assoc', # The target relationship
        'quantity',     # The value of the dictionary
        creator=lambda k, v: OpmOrderItem(item_id=k, quantity=v) # How to create new items
    )

    __mapper_args__ = {'polymorphic_identity': 'OpmOrder'}


class Pallet(Base):
    """
    Represents a pallet in the factory. Maps to the 'pallets' table.
    """
    __tablename__ = 'pallets'

    # Columns in the 'pallets' table
    pallet_id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    destination: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    order_id: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True)
    last_updated_sim_time: Mapped[float] = mapped_column(sqlalchemy.Float)
