from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.base import Base


class Make(Base):
    __tablename__ = "makes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    models = relationship(
        "CarModel",
        back_populates="make",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class CarModel(Base):
    __tablename__ = "car_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    make_id = Column(Integer, ForeignKey("makes.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    make = relationship("Make", back_populates="models", lazy="selectin")
    cars = relationship(
        "Car",
        back_populates="car_model",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String(100), nullable=True)
    car_model_id = Column(Integer, ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=True)
    external_id = Column(String(50), unique=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    car_model = relationship("CarModel", back_populates="cars", lazy="selectin")

    @property
    def full_name(self) -> str:
        """Return a human-friendly car name like 'Toyota Corolla'."""
        if self.car_model and self.car_model.make:
            return f"{self.car_model.make.name} {self.car_model.name}"
        return self.name

