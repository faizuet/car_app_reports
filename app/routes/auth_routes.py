from flask import Blueprint, jsonify
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from webargs.flaskparser import use_kwargs
from marshmallow import ValidationError

from app.schema.user_schema import (
    user_response_schema,
    UserRequestSchema
)

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")


@auth_bp.route('/signup', methods=['POST'])
@use_kwargs(UserRequestSchema, location="json")
def signup(username, email, password):
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "User created successfully",
        "user": user_response_schema.dump(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
@use_kwargs(UserRequestSchema(only=("username", "password")), location="json")
def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.username)
        return jsonify({
            "access_token": access_token,
            "user": user_response_schema.dump(user)
        }), 200

    return jsonify({"msg": "Invalid credentials"}), 401


