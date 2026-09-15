from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.auth_service import login_user, get_current_user, logout_authenticated_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Login route
@auth_bp.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    result = login_user(email,password)
    return result

# Get current user route
@auth_bp.route('/me', methods=["GET"])
@jwt_required()
def me():
    current_user = get_current_user()
    return current_user

# Logout user route
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    logout_user = logout_authenticated_user()
    return logout_user
    