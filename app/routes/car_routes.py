from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.car import Car
from app.schema.car_schema import car_schema, cars_schema
from app.extensions import db
from app.utils.pagination import paginate


car_bp = Blueprint('car', __name__, url_prefix='/api/cars')

@car_bp.route('/', methods=['POST'])
@jwt_required()
def create_car():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    errors = car_schema.validate(json_data)
    if errors:
        return jsonify(errors), 422

    car = Car(**json_data)
    db.session.add(car)
    db.session.commit()

    return car_schema.jsonify(car), 201

@car_bp.route('/', methods=['GET'])
@jwt_required()
@paginate(lambda: Car.query, cars_schema)
def get_all_cars():
    pass

@car_bp.route('/<int:car_id>', methods=['GET'])
@jwt_required()
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return car_schema.jsonify(car), 200

@car_bp.route('/<int:car_id>', methods=['PUT'])
@jwt_required()
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    errors = car_schema.validate(json_data)
    if errors:
        return jsonify(errors), 422

    for key, value in json_data.items():
        setattr(car, key, value)

    db.session.commit()
    return car_schema.jsonify(car), 200

@car_bp.route('/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted successfully"}), 200

