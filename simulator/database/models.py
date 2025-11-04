import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class all models inherit from"""
    pass

class Pallet(Base):
    """
    Represents a pallet in the factory. Maps to the 'pallets' table.
    """
    __tablename__ = 'pallets'

    # Columns in the 'pallets' table
    id: Mapped[str] = mapped_column(primary_key=True)
    contents: Mapped[str] = mapped_column(sqlalchemy.String, default="Empty")
    current_location: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    last_updated_sim_time: Mapped[float] = mapped_column(sqlalchemy.Float)

