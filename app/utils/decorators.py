from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import jsonify

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims.get("role") != required_role:
                return jsonify({"msg": "Forbidden - Insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
