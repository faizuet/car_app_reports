import logging
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from marshmallow import Schema, fields

from app.models.user import User
from app.utils.auth import get_user_by_email, commit_instance
from app.schema.user_schema import UserSchema, LoginSchema, user_response_schema

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


class SignupResponseSchema(Schema):
    message = fields.String(required=True)
    user = fields.Nested(user_response_schema, required=True)


class TokenSchema(Schema):
    access_token = fields.String(required=True)


@auth_bp.route("/signup", methods=["POST"])
@auth_bp.arguments(UserSchema)
@auth_bp.response(201, SignupResponseSchema)
def signup(data):
    if get_user_by_email(data["email"]):
        logger.info(f"Signup blocked — email exists: {data['email']}")
        abort(409, message="User already exists")

    user = User(username=data["username"], email=data["email"])
    user.password = data["password"]

    success, error = commit_instance(user)
    if success:
        logger.info(f"New user created: {user.email} (id={user.id})")
        return {"message": "User created successfully", "user": user}

    logger.error(f"Signup failed for {data['email']} — {error}")
    abort(500, message="Internal server error")


@auth_bp.route("/login", methods=["POST"])
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, TokenSchema)
def login(data):
    user = get_user_by_email(data["email"])
    if user and user.check_password(data["password"]):
        logger.info(f"User login successful: {user.email} (id={user.id})")
        token = create_access_token(identity=str(user.id))
        return {"access_token": token}

    logger.warning(f"Invalid login attempt: {data['email']}")
    abort(401, message="Invalid credentials")

