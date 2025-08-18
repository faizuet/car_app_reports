from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, ma, jwt, migrate
from marshmallow import ValidationError
from app.routes.user_routes import user_bp
from app.routes.car_routes import car_bp
from app.routes.auth_routes import auth_bp

from app.models import User, Car, CarModel

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify({"errors": err.messages}), 422

    app.register_blueprint(car_bp, url_prefix="/api/cars")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/auth")


    return app

