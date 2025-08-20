import logging
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.car import Car, CarModel, Make
from app.schema.car_schema import CarSchema, CarCreateSchema, CarUpdateSchema

logger = logging.getLogger(__name__)
car_bp = Blueprint("car", __name__, description="Car related operations")


@car_bp.route("/", methods=["POST"])
@jwt_required()
@car_bp.arguments(CarCreateSchema)
@car_bp.response(201, CarSchema)
def create_car(data):
    try:
        make_name = data.get("make")
        model_name = data.get("model")

        make = db.session.query(Make).filter_by(name=make_name).first()
        if not make:
            make = Make(name=make_name)
            db.session.add(make)
            db.session.flush()

        model = None
        if model_name:
            model = db.session.query(CarModel).filter_by(name=model_name, make_id=make.id).first()
            if not model:
                model = CarModel(name=model_name, make_id=make.id)
                db.session.add(model)
                db.session.flush()

        car = Car(
            make_id=make.id,
            model_id=model.id if model else None,
            year=data["year"],
            category=data.get("category")
        )
        db.session.add(car)
        db.session.commit()
        logger.info(f"Car created successfully: {car.id}")
        return car

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating car: {str(e)}")
        abort(400, message="Could not create car")


@car_bp.route("/", methods=["GET"])
@jwt_required()
@car_bp.response(200, CarSchema(many=True))
def get_all_cars():
    try:
        cars = db.session.query(Car).all()
        return cars
    except SQLAlchemyError as e:
        logger.error(f"Error fetching cars: {str(e)}")
        abort(500, message="Could not fetch cars")


@car_bp.route("/<int:car_id>", methods=["GET"])
@jwt_required()
@car_bp.response(200, CarSchema)
def get_car(car_id):
    try:
        car = db.session.get(Car, car_id)
        if not car:
            abort(404, message=f"Car with ID {car_id} not found")
        return car
    except SQLAlchemyError as e:
        logger.error(f"Error fetching car {car_id}: {str(e)}")
        abort(500, message="Could not fetch car")


@car_bp.route("/<int:car_id>", methods=["PATCH"])
@jwt_required()
@car_bp.arguments(CarUpdateSchema)
@car_bp.response(200, CarSchema)
def update_car(data, car_id):
    try:
        car = db.session.get(Car, car_id)
        if not car:
            abort(404, message=f"Car with ID {car_id} not found")

        # Update fields
        for key in ["year", "category"]:
            if key in data:
                setattr(car, key, data[key])

        if "make" in data:
            make_name = data["make"]
            make = db.session.query(Make).filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                db.session.add(make)
                db.session.flush()
            car.make_id = make.id

        if "model" in data:
            model_name = data["model"]
            model = db.session.query(CarModel).filter_by(name=model_name, make_id=car.make_id).first()
            if not model:
                model = CarModel(name=model_name, make_id=car.make_id)
                db.session.add(model)
                db.session.flush()
            car.model_id = model.id

        db.session.commit()
        logger.info(f"Car updated successfully: {car.id}")
        return car

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating car {car_id}: {str(e)}")
        abort(400, message="Could not update car")


@car_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
@car_bp.response(200, dict)
def delete_car(car_id):
    try:
        car = db.session.get(Car, car_id)
        if not car:
            abort(404, message=f"Car with ID {car_id} not found")

        db.session.delete(car)
        db.session.commit()
        logger.info(f"Car deleted successfully: {car.id}")
        return {"message": f"Car with ID {car_id} deleted successfully"}

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting car {car_id}: {str(e)}")
        abort(400, message="Could not delete car")

