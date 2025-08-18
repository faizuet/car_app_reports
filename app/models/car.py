from datetime import datetime, timezone
from app import db

class Car(db.Model):
    __tablename__ = 'cars'

    __table_args__ = (
        db.UniqueConstraint('objectId', name='uq_cars_object_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String(50), unique=True, nullable=False)
    objectId = db.Column(db.String(255), nullable=False, unique=True)
    make = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(100), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    models = db.relationship(
        "CarModel",
        back_populates="car",
        cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_car_id():
        last_car = Car.query.order_by(Car.id.desc()).first()
        if last_car and last_car.car_id:
            try:
                last_num = int(last_car.car_id.replace("CAR-", ""))
            except ValueError:
                last_num = last_car.id
        else:
            last_num = 0
        return f"CAR-{last_num + 1:04d}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.car_id:
            self.car_id = Car.generate_car_id()


class CarModel(db.Model):
    __tablename__ = 'car_models'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    trim = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship("Car", back_populates="models")

