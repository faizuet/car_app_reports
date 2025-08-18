from flask import request, jsonify
from functools import wraps

def paginate(query_fn, schema, default_limit=10):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                query = query_fn(*args, **kwargs)
                page = request.args.get('page', 1, type=int)
                limit = request.args.get('limit', default_limit, type=int)

                pagination = query.paginate(page=page, per_page=limit, error_out=False)
                data = schema.dump(pagination.items, many=True)

                return jsonify({
                    "message": "Data retrieved successfully",
                    "data": data,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "current_page": pagination.page,
                    "limit": limit
                }), 200

            except Exception as e:
                return jsonify({"message": f"Pagination failed: {str(e)}"}), 500

        return wrapper
    return decorator
