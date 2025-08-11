from flask import request, jsonify
from functools import wraps

class PaginationHelper:
    """
    Helper class to handle pagination logic using Flask-SQLAlchemy's `paginate`.
    """

    def __init__(self, query, schema, default_limit=10):
        self.query = query
        self.schema = schema
        self.page = request.args.get('page', 1, type=int)
        self.limit = request.args.get('limit', default_limit, type=int)

    def paginate(self):
        pagination = self.query.paginate(page=self.page, per_page=self.limit, error_out=False)
        serialized_data = self.schema.dump(pagination.items, many=True)

        return {
            "data": serialized_data,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "limit": self.limit
        }


def paginate(query_fn, schema):
    """
    Decorator to apply pagination to a route.

    Args:
        query_fn (function): Function that returns a SQLAlchemy query.
        schema (Schema): Marshmallow schema instance.

    Usage:
        @paginate(lambda: Model.query, model_schema)
        def get_models(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                query = query_fn(*args, **kwargs)
                paginator = PaginationHelper(query, schema)
                result = paginator.paginate()
                return jsonify({
                    "message": "Data retrieved successfully",
                    **result
                }), 200
            except Exception as e:
                return jsonify({"message": f"Pagination failed: {str(e)}"}), 500
        return wrapper
    return decorator
