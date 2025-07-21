from flask import Blueprint, jsonify, request
from app.services.parse_services import fetch_all_cars
from app.models.car import Car
from app import db

car_bp = Blueprint('car_bp', __name__)

@car_bp.route('/')
def home():
    return jsonify(message="🚗 Car API is running! Use /cars or /sync to get started.")

# Sync from Parse API
@car_bp.route('/sync', methods=['GET'])
def sync_cars():
    cars_data = fetch_all_cars()
    count = 0
    for item in cars_data:
        if int(item.get("Year", 0)) < 2012 or int(item.get("Year", 0)) > 2022:
            continue
        existing = Car.query.filter_by(object_id=item["objectId"]).first()
        if not existing:
            car = Car(
                object_id=item["objectId"],
                make=item.get("Make", ""),
                model=item.get("Model", ""),
                year=item.get("Year", "")
            )
            db.session.add(car)
            count += 1
    db.session.commit()
    return jsonify(message=f"{count} new cars synced successfully.")

# READ all cars
@car_bp.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    return jsonify([
        {"id": car.id, "object_id": car.object_id, "make": car.make, "model": car.model, "year": car.year}
        for car in cars
    ])

# CREATE a new car
@car_bp.route('/cars', methods=['POST'])
def create_car():
    data = request.json
    car = Car(
        object_id=data.get('object_id', ''),  # optional for manual create
        make=data['make'],
        model=data['model'],
        year=data['year']
    )
    db.session.add(car)
    db.session.commit()
    return jsonify(message="Car created successfully.", id=car.id), 201

# UPDATE an existing car
@car_bp.route('/cars/<int:id>', methods=['PUT'])
def update_car(id):
    car = Car.query.get_or_404(id)
    data = request.json
    car.make = data.get('make', car.make)
    car.model = data.get('model', car.model)
    car.year = data.get('year', car.year)
    db.session.commit()
    return jsonify(message="Car updated successfully.")

# DELETE a car
@car_bp.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    return jsonify(message="Car deleted successfully.")
