from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt
from .response import api_response

def role_required(*roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return api_response("error", 403, "You do not have permission to access this resource.")
            return function(*args, **kwargs)
        return wrapper
    return decorator