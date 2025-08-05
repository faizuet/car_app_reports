from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from app.schema.user_schema import user_schema, user_response_schema
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username already exists"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered"}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "User created successfully",
        "user": user_response_schema.dump(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = user_schema.load(request.get_json(), partial=("email",))
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({
            "access_token": access_token,
            "user": user_response_schema.dump(user)
        }), 200

    return jsonify({"msg": "Invalid credentials"}), 401
