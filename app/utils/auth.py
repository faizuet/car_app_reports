import logging
from flask import jsonify
from app.extensions import db

logger = logging.getLogger(__name__)

def get_user_by_email(email):
    from app.models.user import User
    return User.query.filter_by(email=email).first()

def commit_instance(instance):
    try:
        db.session.add(instance)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"DB commit error: {e}")
        return False, str(e)

def json_response(payload, status_code=200):
    return jsonify(payload), status_code
