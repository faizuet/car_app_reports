from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.schema.user_schema import user_response_schema, UserUpdateSchema
from app.extensions import db

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@user_bp.response(200, user_response_schema)
def profile():
    """Get current user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return user


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
@user_bp.arguments(UserUpdateSchema)
@user_bp.response(200, user_response_schema)
def update_profile(data):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if not data:
        return {"message": "No fields provided for update"}, 400

    for key, value in data.items():
        if key == "password":
            user.password = value
        elif hasattr(user, key):
            setattr(user, key, value)

    db.session.commit()
    return user

