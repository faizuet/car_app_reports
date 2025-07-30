from flask import Flask
from app.extensions import db, jwt, migrate  # ✅
from app.routes.car_routes import car_bp
from app.routes.auth_routes import auth_bp
from app.models import user, car  # ✅ make sure models are imported

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/cars.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # ✅

    app.register_blueprint(car_bp)
    app.register_blueprint(auth_bp)

    return app

# this is comment
