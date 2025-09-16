from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base


class Make(Base):
    __tablename__ = "makes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    models: Mapped[List["CarModel"]] = relationship(
        "CarModel",
        back_populates="make",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    make_id: Mapped[int] = mapped_column(ForeignKey("makes.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    make: Mapped["Make"] = relationship("Make", back_populates="models", lazy="selectin")
    cars: Mapped[List["Car"]] = relationship(
        "Car",
        back_populates="car_model",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    car_model_id: Mapped[int] = mapped_column(ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    car_model: Mapped["CarModel"] = relationship("CarModel", back_populates="cars", lazy="selectin")

    @property
    def full_name(self) -> str:
        """Return a human-friendly car name like 'Toyota Corolla'."""
        if self.car_model and self.car_model.make:
            return f"{self.car_model.make.name} {self.car_model.name}"
        return self.name

