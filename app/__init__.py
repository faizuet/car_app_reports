from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)

    # Register Blueprints
    from app.routes.car_routes import car_bp
    app.register_blueprint(car_bp)

    with app.app_context():
        from app.models.car import Car
        db.create_all()

    return app
