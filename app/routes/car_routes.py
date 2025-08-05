from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.car import Car
from app.extensions import db
from app.schema.car_schema import car_schema, cars_schema
from app.services.parse_services import fetch_all_cars

car_bp = Blueprint('cars', __name__)

@car_bp.route('/')
def home():
    return jsonify({"message": "Car API is running! Use /cars to interact with the API."})

@car_bp.route('/cars', methods=['GET'])
@jwt_required()
def get_cars():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        pagination = Car.query.paginate(page=page, per_page=limit, error_out=False)
        cars = cars_schema.dump(pagination.items)
        return jsonify({
            "message": "Cars retrieved successfully",
            "cars": cars,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        }), 200
    except Exception as e:
        return jsonify({"message": f"Failed to retrieve cars. Error: {str(e)}"}), 500

@car_bp.route('/cars/<int:car_id>', methods=['GET'])
@jwt_required()
def get_car(car_id):
    car = Car.query.get(car_id)
    if car:
        return jsonify(car_schema.dump(car)), 200
    return jsonify({"msg": "Car not found"}), 404

@car_bp.route('/cars', methods=['POST'])
@jwt_required()
def create_car():
    try:
        data = car_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    car = Car(**data)
    db.session.add(car)
    db.session.commit()
    return jsonify(car_schema.dump(car)), 201

@car_bp.route('/sync', methods=['GET'])
@jwt_required()
def sync_cars():
    try:
        cars_data = fetch_all_cars()
        created, updated = 0, 0
        for data in cars_data:
            parse_id = data.get("parse_id")
            if not parse_id:
                continue

            existing = Car.query.filter_by(parse_id=parse_id).first()
            if existing:
                existing.make = data.get("make")
                existing.model = data.get("model")
                existing.year = data.get("year")
                existing.created_at = data.get("created_at")
                updated += 1
            else:
                car = Car(
                    parse_id=parse_id,
                    make=data.get("make"),
                    model=data.get("model"),
                    year=data.get("year"),
                    created_at=data.get("created_at")
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
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"msg": "Car not found"}), 404
    try:
        data = car_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    for key, value in data.items():
        setattr(car, key, value)
    db.session.commit()
    return jsonify(car_schema.dump(car)), 200

@car_bp.route('/cars/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"msg": "Car not found"}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({"msg": "Car deleted"}), 200
