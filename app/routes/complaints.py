from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.utils.auth import role_required

from app.controllers import ComplaintController

complaints_bp = Blueprint("complaints", __name__, url_prefix="/api/complaints")
complaint_controller = ComplaintController()

# Add a new complaint route
@complaints_bp.route('/add', methods=["POST"])
@jwt_required()
def add_new_complaint():
    result = complaint_controller.add_complaint()
    return result

# Get list of complaints route
@complaints_bp.route("/list", methods=["GET"])
@jwt_required()
def get_complaints():
    result = complaint_controller.get_complaints()
    return result

# Get details of a specific complaint route
@complaints_bp.route("/show", methods=["GET"])
@jwt_required()
def get_complaint_details():
    result = complaint_controller.get_complaint()
    return result

# Update details of a complaint route
@complaints_bp.route("/update", methods=["PATCH"])
@jwt_required()
def update_complaint_details():
    result = complaint_controller.update_complaint()
    return result

# Assign complaint to a staff route
@complaints_bp.route('/assign', methods=["PUT"])
@jwt_required()
@role_required("admin")
def assign_complaint():
    result = complaint_controller.assign_complaint()
    return result

# Update complaint status route
@complaints_bp.route("/update-status", methods=["PUT"])
@jwt_required()
@role_required("admin", "staff")
def update_complaint_status():
    result = complaint_controller.update_complaint_status()
    return result

# Add resolution notes to the complaint route
@complaints_bp.route("/resolution-note", methods=["PUT"])
@jwt_required()
@role_required("admin", "staff")
def add_complaint_resolution_notes():
    result = complaint_controller.add_resolution_notes()
    return result

