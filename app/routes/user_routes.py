import logging
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user import User
from app.schema.user_schema import user_response_schema, UserSchema
from app.extensions import db

logger = logging.getLogger(__name__)
user_bp = Blueprint("user", __name__, description="User related operations")


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@user_bp.response(200, user_response_schema)
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user
    except SQLAlchemyError as e:
        logger.error(f"Error fetching profile: {str(e)}")
        abort(500, message="Could not fetch user profile")


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
@user_bp.arguments(UserSchema(partial=True))
@user_bp.response(200, user_response_schema)
def update_profile(data):
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        if not data:
            abort(400, message="No fields provided for update")

        for key, value in data.items():
            if key == "password":
                user.password = value
            elif hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

    except IntegrityError as e:
        db.session.rollback()
        logger.warning(f"Conflict updating user {user_id}: {str(e)}")
        abort(409, message="Update conflicts with existing data")

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        abort(500, message="Could not update user profile")

