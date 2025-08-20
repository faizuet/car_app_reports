from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.db import Base

class Make(Base):
    __tablename__ = "makes"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)

class CarModel(Base):
    __tablename__ = "car_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    make_id = Column(Integer, ForeignKey("makes.id"))
    make = relationship("Make")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    make_id = Column(Integer, ForeignKey("makes.id"))
    model_id = Column(Integer, ForeignKey("car_models.id"))
    year = Column(Integer, nullable=False)
    category = Column(String(64))

    make = relationship("Make")
    model = relationship("CarModel")

