from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_json(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            json_data = request.get_json()
            if not json_data:
                return jsonify({"message": "No input data provided"}), 400
            try:
                data = schema.load(json_data)
            except ValidationError as err:
                return jsonify(err.messages), 422
            return fn(data, *args, **kwargs)
        return wrapper
    return decorator
