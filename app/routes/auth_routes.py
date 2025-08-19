import logging
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.extensions import db
from app.models.user import User
from app.schema.user_schema import (
    UserSchema,
    user_response_schema,
    user_login_schema
)

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, description="Authentication operations")


@auth_bp.route("/signup", methods=["POST"])
@auth_bp.arguments(UserSchema)
@auth_bp.response(201, user_response_schema)
def signup(data):
    try:
        username = data["username"].strip()
        email = data["email"].strip()
        password = data["password"].strip()


        existing_user = db.session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            abort(409, message="Username or email already exists. Please choose another.")


        user = User(username=username, email=email)
        user.password = password

        db.session.add(user)
        db.session.commit()

        logger.info(f"User created successfully: {user.username} ({user.id})")


        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }

    except IntegrityError as e:
        db.session.rollback()
        logger.warning(f"Integrity error during signup: {str(e)}")
        abort(409, message="Username or email already exists.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Signup error: {str(e)}")
        abort(500, message="Internal server error")


@auth_bp.route("/login", methods=["POST"])
@auth_bp.arguments(user_login_schema)
@auth_bp.response(200, user_response_schema)
def login(data):
    try:
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        user = db.session.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for email: {email}")
            abort(401, message="Invalid credentials")


        token = create_access_token(identity=str(user.id))
        logger.info(f"User logged in successfully: {user.username} ({user.id})")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token
        }

    except SQLAlchemyError as e:
        logger.error(f"Login error: {str(e)}")
        abort(500, message="Internal server error")

