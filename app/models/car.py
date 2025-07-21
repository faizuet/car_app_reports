from app import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.String(100), unique=True)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(4))
