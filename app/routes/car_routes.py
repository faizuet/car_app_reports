from flask import Blueprint, jsonify, request
from app.models.car import Car
from app.extensions import db
from flask_jwt_extended import jwt_required

car_bp = Blueprint('cars', __name__)

# ✅ Root Route - Now you won't get "Not Found" at /
@car_bp.route('/')
def home():
    return jsonify({"message": " Car API is running! Use /cars to list all cars."})

@car_bp.route('/cars', methods=['GET'])
@jwt_required()
def get_cars():
    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars]), 200

@car_bp.route('/cars/<int:car_id>', methods=['GET'])
@jwt_required()
def get_car(car_id):
    car = Car.query.get(car_id)
    if car:
        return jsonify(car.to_dict()), 200
    return jsonify({"msg": "Car not found"}), 404

@car_bp.route('/cars', methods=['POST'])
@jwt_required()
def create_car():
    data = request.get_json()
    car = Car(
        object_id=data['object_id'],
        make=data['make'],
        model=data['model'],
        year=data['year'],
        created_at=data['created_at']
    )
    db.session.add(car)
    db.session.commit()
    return jsonify(car.to_dict()), 201

from app.services.parse_services import fetch_all_cars

@car_bp.route('/sync', methods=['GET'])
def sync_cars():
    try:
        cars_data = fetch_all_cars()
        created, updated = 0, 0

        for data in cars_data:
            existing = Car.query.filter_by(object_id=data["object_id"]).first()
            if existing:
                # Update existing car
                existing.make = data["make"]
                existing.model = data["model"]
                existing.year = data["year"]
                existing.created_at = data["created_at"]
                updated += 1
            else:
                # Create new car
                car = Car(
                    object_id=data["object_id"],
                    make=data["make"],
                    model=data["model"],
                    year=data["year"],
                    created_at=data["created_at"]
                )
                db.session.add(car)
                created += 1

        db.session.commit()
        return jsonify({"msg": f"{created} new cars added, {updated} updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@car_bp.route('/cars/<int:car_id>', methods=['PUT'])
@jwt_required()
def update_car(car_id):
    data = request.get_json()
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"msg": "Car not found"}), 404

    car.make = data.get('make', car.make)
    car.model = data.get('model', car.model)
    car.year = data.get('year', car.year)
    car.created_at = data.get('created_at', car.created_at)

    db.session.commit()
    return jsonify(car.to_dict()), 200

@car_bp.route('/cars/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"msg": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return jsonify({"msg": "Car deleted"}), 200
