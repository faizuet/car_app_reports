from flask import Flask
from app.config import Config
from app.extensions import db, ma, jwt, migrate
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config["broker_url"] = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    app.config["result_backend"] = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.routes.car_routes import car_bp
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(car_bp)
    app.register_blueprint(auth_bp)

    return app

