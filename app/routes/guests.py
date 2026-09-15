from flask import Blueprint
from app.controllers import GuestController

guests_bp = Blueprint("guests", __name__, url_prefix="/api/guest")
guest_controller = GuestController()

# Login route
@guests_bp.route("/login", methods=["POST"])
def login_guest():
    result = guest_controller.login_guests()
    return result
                 
