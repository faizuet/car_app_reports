from app import db

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    parse_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return f"<Car {self.name or self.make}>"
