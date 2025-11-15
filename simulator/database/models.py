import sqlalchemy
from sqlalchemy import ForeignKey
from simulator.core.orders.order import OrderStatus
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy


class Base(DeclarativeBase):
    """Base class all models inherit from"""
    pass


class Item(Base):
    """
    Represents an item in the factory catalogue. Maps to the 'items' table.
    This table holds the master data for all stock keeping units.
    """
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(100), unique=True, nullable=False)
    weight: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=False)
    category: Mapped[str] = mapped_column(sqlalchemy.String(50), nullable=False)
    volume: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=False)
    stackable: Mapped[bool] = mapped_column(sqlalchemy.Boolean, nullable=False)

class Order(Base):
    """
    SQLAlchemy model for the base 'orders' table.
    """
    __tablename__ = 'orders'

    # Columns common to all orders
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sqlalchemy.String) # Discriminator column
    order_time: Mapped[float] = mapped_column(sqlalchemy.Float)
    completion_time: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=True, default=None)
    status: Mapped[OrderStatus] = mapped_column(sqlalchemy.Enum(OrderStatus,
            name="orderstatus",
            values_callable=lambda obj: [e.value for e in obj],
            native_enum=False), default=OrderStatus.PENDING)

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
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), nullable=False)
    qty: Mapped[int] = mapped_column(sqlalchemy.Integer)

    # Relationship to the Item object
    item: Mapped['Item'] = relationship(lazy="joined")

    __mapper_args__ = {'polymorphic_identity': 'RefillOrder'}


class OpmOrderItem(Base):
    """Stores the key-value pairs from the OpmOrder.items dictionary."""
    __tablename__ = 'opm_order_items'
    id: Mapped[int] = mapped_column(ForeignKey('opm_orders.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=False, default=0)

    # Relationship to the Item object
    item: Mapped['Item'] = relationship(lazy="joined")


class OpmOrder(Order):
    """
    SQLAlchemy model for the 'opm_orders' table.
    Inherits from the Order model.
    """
    __tablename__ = 'opm_orders'

    id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    _items_assoc: Mapped[dict[int, OpmOrderItem]] = relationship(
        collection_class=attribute_mapped_collection('item_id'),
        cascade="all, delete-orphan",
    )
    items: dict[int, int] = association_proxy(
        target_collection='_items_assoc',
        attr='quantity',
        creator=lambda k, v: OpmOrderItem(item_id=k, quantity=v)
    )

    __mapper_args__ = {'polymorphic_identity': 'OpmOrder'}


class Pallet(Base):
    """
    Represents a pallet in the factory. Maps to the 'pallets' table.
    """
    __tablename__ = 'pallets'

    # Columns in the 'pallets' table
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    destination: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True, default=None)
    order_id: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True, default=None)
    stored: Mapped[bool] = mapped_column(sqlalchemy.Boolean, nullable=False, default=True)
    last_updated_sim_time: Mapped[float] = mapped_column(sqlalchemy.Float, nullable=False)
