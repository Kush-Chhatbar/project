from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.utils.auth import role_required
from app.controllers.complaint_category_controller import ComplaintCategoryController
from app.analytics.complaint_category_analytics import ComplaintCategoryAnalytics

complaint_categories_bp = Blueprint("complaint_categories", __name__, url_prefix="/api/complaint-category")
complaint_category_controller = ComplaintCategoryController()
complaint_category_analytics = ComplaintCategoryAnalytics()

# Get all complaint categories route
@complaint_categories_bp.route("/list", methods=["GET"])
@jwt_required()
def list_complaint_categories():
    result = complaint_category_controller.get_complaint_categories()
    return result

# Get details of a particular complaint category route
@complaint_categories_bp.route("/show", methods=["GET"])
@jwt_required()
def show_complaint_category():
    result = complaint_category_controller.get_complaint_category()
    return result

# Add complaint category route
@complaint_categories_bp.route('/add', methods=["POST"])
@jwt_required()
@role_required("admin")
def store_complaint_category():
    result = complaint_category_controller.create_complaint_category()
    return result

# Delete department route
@complaint_categories_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_department():
    result = complaint_category_controller.delete_complaint_category()
    return result

# Activate department route
@complaint_categories_bp.route("/activate", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def activate_department():
   result = complaint_category_controller.activate_department()
   return result

# Analyze complaint category data
@complaint_categories_bp.route("/analytics", methods=["GET"])
@jwt_required()
@role_required("admin")
def analyze_categories():
    result = complaint_category_analytics.get_category_analytics()
    return result
