from flask import request
from flask.blueprints import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import FeedbackController
from app.utils.auth import role_required
from app.analytics.feedback_analytics import FeedbackAnalytics
from app.utils.auth import api_response


feedbacks_bp = Blueprint("feedbacks", __name__, url_prefix="/api/feedback")
feedback_controller = FeedbackController()
feedback_analysis = FeedbackAnalytics()

# Add a new feedback route
@feedbacks_bp.route('/add', methods=["POST"])
@jwt_required()
def add_feedback():
    result = feedback_controller.add_new_feedback()
    return result

# Get all feedbacks route
@feedbacks_bp.route('/list', methods=["GET"])
@jwt_required()
def get_feedbacks():
    result = feedback_controller.get_feedbacks()
    return result

# Get specific feedback details route
@feedbacks_bp.route("/show", methods=["GET"])
@jwt_required()
def show_feedback_details():
    result = feedback_controller.get_feedback()
    return result

# Get analysis of the feedback data route
@feedbacks_bp.route("/analytics", methods=["GET"])
@jwt_required()
@role_required("admin")
def show_feedback_analytics():
    try:
        result = feedback_analysis.get_analytics()
        return api_response("success", 200, "Feedback analytics fetched successfully", result)

    except Exception as e:
        return api_response("error",500,str(e))

# Trend based analytics of the feedback route.
@feedbacks_bp.route("/analytics/trend", methods=["GET"])
@jwt_required()
@role_required("admin")
def show_feedback_trend():
    try:
        period = request.args.get("period","monthly").lower()
        trend = (feedback_analysis.get_feedback_trend(period))
        return api_response("success",200,"Feedback trend fetched successfully",trend)
    except ValueError as e:
        return api_response("error",400,str(e))
    except Exception as e:
        return api_response("error",500,str(e))