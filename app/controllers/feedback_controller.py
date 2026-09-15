from flask import request

from app.services.feedback_service import FeedbackService

class FeedbackController:
    def __init__(self):
        self.feedback_service = FeedbackService()

    # Add a new feedback
    def add_new_feedback(self):
        data = request.get_json()
        return self.feedback_service.add_feedback(data)

    # Get list of all the feedbacks
    def get_feedbacks(self):
        rating_range = request.args.get("rating_range")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        return self.feedback_service.get_feedbacks(rating_range=rating_range,from_date=from_date,to_date=to_date)

    # Get details of a specific feedback
    def get_feedback(self):
        feedback_id = request.args.get("feedback_id")
        return self.feedback_service.get_feedback_details(feedback_id)