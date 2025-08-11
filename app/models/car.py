from datetime import datetime, timezone
from app import db

class Car(db.Model):
    __tablename__ = 'cars'

    __table_args__ = (
        db.UniqueConstraint('objectId', name='uq_cars_object_id'),
    )

    ID_KEY = 'id'
    CAR_ID_KEY = 'car_id'
    NAME_KEY = 'name'
    MAKE_KEY = 'make'
    MODEL_KEY = 'model'
    YEAR_KEY = 'year'
    CATEGORY_KEY = 'category'
    CREATED_AT_KEY = 'created_at'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String(50), unique=True, nullable=False)
    objectId = db.Column(db.String, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    make = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Car {self.name or self.make}>"

    def to_json(self):
        return {
            self.ID_KEY: self.id,
            self.CAR_ID_KEY: self.car_id,
            self.NAME_KEY: self.name,
            self.MAKE_KEY: self.make,
            self.MODEL_KEY: self.model,
            self.YEAR_KEY: self.year,
            self.CATEGORY_KEY: self.category,
            self.CREATED_AT_KEY: self.created_at.isoformat() if self.created_at else None
        }

