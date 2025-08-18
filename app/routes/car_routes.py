from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.car import Car, CarModel
from app.schema.car_schema import CarSchema
from app.extensions import db
from app.utils.pagination import paginate
from app.utils.validation import validate_json

car_bp = Blueprint("car", __name__)

car_schema = CarSchema()
cars_schema = CarSchema(many=True)


@car_bp.route("/", methods=["POST"])
@jwt_required()
@validate_json(car_schema)
def create_car(data):
    models_data = data.pop("models", [])
    car = Car(**data)
    for model_data in models_data:
        car.models.append(CarModel(**model_data))

    db.session.add(car)
    db.session.commit()
    return car_schema.jsonify(car), 201


@car_bp.route("/", methods=["GET"])
@jwt_required()
@paginate(lambda: Car.query, cars_schema)
def get_all_cars():
    pass


@car_bp.route("/<int:car_id>", methods=["GET"])
@jwt_required()
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return car_schema.jsonify(car), 200


@car_bp.route("/<int:car_id>", methods=["PUT"])
@jwt_required()
@validate_json(car_schema)
def update_car(data, car_id):
    car = Car.query.get_or_404(car_id)

    for key, value in data.items():
        if key != "models":
            setattr(car, key, value)

    if "models" in data:
        car.models.clear()
        for model_data in data["models"]:
            car.models.append(CarModel(**model_data))

    db.session.commit()
    return car_schema.jsonify(car), 200


@car_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted successfully"}), 200

