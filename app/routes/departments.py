from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.utils.auth import role_required
from app.controllers.department_controller import DepartmentController

from app.analytics.department_analytics import DepartmentAnalytics

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")
department_controller = DepartmentController()
department_analytics = DepartmentAnalytics()

# Add department route
@departments_bp.route("/add", methods=["POST"])
@jwt_required()
@role_required("admin")
def store_department():
    result = department_controller.create_department()
    return result

# Get all departments route
@departments_bp.route("/list", methods=["GET"])
@jwt_required()
def list_departments():
    result = department_controller.get_departments()
    return result

# Get specific department details route
@departments_bp.route("/show", methods=["GET"])
@jwt_required()
def show_department_details():
    result = department_controller.get_department()
    return result

# Update department route
@departments_bp.route("/update", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def update_department():
    result = department_controller.update_department()
    return result

# Delete department route
@departments_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_department():
    result = department_controller.delete_department()
    return result

# Activate department route
@departments_bp.route("/activate", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def activate_department():
   result = department_controller.activate_department()
   return result

# Department analytics data route
@departments_bp.route("/analytics", methods=["GET"])
@jwt_required()
@role_required("admin")
def analyze_department():
    result = department_analytics.get_department_performance()
    return result