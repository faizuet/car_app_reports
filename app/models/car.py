from app.extensions import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.String(100), unique=True, nullable=False)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    created_at = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "object_id": self.object_id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "created_at": self.created_at,
        }
