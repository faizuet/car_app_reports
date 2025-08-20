from flask_jwt_extended import verify_jwt_in_request
from functools import wraps
from flask import jsonify

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"msg": "Unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper
