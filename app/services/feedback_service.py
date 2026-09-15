from app.extensions import db
from app.models import Feedback, Department
from app.models import DepartmentFeedback
from app.utils.response import api_response
from flask_jwt_extended import get_jwt, get_jwt_identity
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime
from app.constants.notification_types import LOW_RATING_THRESHOLD, LOW_RATING
from app.services.notification_service import notification_service

class FeedbackService:

    # Add a new feedback
    def add_feedback(self, data):
        # Get logged-in guest information from JWT
        claims = get_jwt()
        guest_id = get_jwt_identity()
        stay_id = claims.get("stay_id")

        if not stay_id:
            return api_response("error",400,"Guest stay information is missing.")

        # Get overall feedback ratings
        cleanliness_rating = data.get("cleanliness_rating")
        staff_rating = data.get("staff_rating")
        food_rating = data.get("food_rating")
        service_rating = data.get("service_rating")
        comment = data.get("comment")

        required_ratings = {
            "cleanliness_rating": cleanliness_rating,
            "staff_rating": staff_rating,
            "food_rating": food_rating,
            "service_rating": service_rating
        }

        rating_labels = {
            "cleanliness_rating": "Cleanliness rating",
            "staff_rating": "Staff rating",
            "food_rating": "Food rating",
            "service_rating": "Service rating"
        }

        # Validate overall ratings
        validated_ratings = {}

        for field, rating in required_ratings.items():
            label = rating_labels[field]
            if rating is None:
                return api_response("error",400,f"{label} is required.")
            
            try:
                rating = Decimal(str(rating))
            except (InvalidOperation, TypeError, ValueError):
                return api_response("error",400,f"{label} must be a valid number.")

            if rating < Decimal("1.0") or rating > Decimal("5.0"):
                return api_response("error",400,f"{label} must be between 1.0 and 5.0.")

            if rating.as_tuple().exponent < -1:
                return api_response("error",400,f"{label} can have only one value after decimal point.")

            validated_ratings[field] = rating

        cleanliness_rating = validated_ratings["cleanliness_rating"]
        staff_rating = validated_ratings["staff_rating"]
        food_rating = validated_ratings["food_rating"]
        service_rating = validated_ratings["service_rating"]

        # Validate department feedback
        department_feedback_data = data.get("department_feedback", [])

        if not isinstance(department_feedback_data, list):
            return api_response("error",400,"Department feedback must be an array.")

        department_ids = set()
        validated_department_feedback = []

        for item in department_feedback_data:
            department_id = item.get("department_id")
            rating = item.get("rating")
            department_comment = item.get("comment")

            # Department ID required
            if department_id is None:
                return api_response("error",400,"Department ID is required.")

            # Prevent duplicate department feedback
            if department_id in department_ids:
                return api_response("error",400,"Feedback for the same department cannot be submitted twice.")

            department_ids.add(department_id)

            # Check department exists
            department = Department.query.get(department_id)
            if not department:
                return api_response("error",400,f"Department with ID {department_id} does not exist.")

            # Validate department rating
            if rating is None:
                return api_response("error",400,f"Rating is required for department {department.name}.")

            try:
                rating = Decimal(str(rating))
            except (InvalidOperation, TypeError, ValueError):
                return api_response("error",400,f"Rating for {department.name} must be a valid number.")

            if rating < Decimal("1.0") or rating > Decimal("5.0"):
                return api_response("error",400,f"Rating for {department.name} must be between 1.0 and 5.0.")

            if rating.as_tuple().exponent < -1:
                return api_response("error",400,f"Rating for {department.name} can have only one value after decimal point.")

            validated_department_feedback.append({
                "department_id": department_id,
                "rating": rating,
                "comment": department_comment
            })

        # Calculate overall rating
        overall_rating_calculated = (
            cleanliness_rating
            + staff_rating
            + food_rating
            + service_rating
        ) / Decimal("4")

        overall_rating = overall_rating_calculated.quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP
        )

        # Create main feedback

        feedback = Feedback(
            guest_id=guest_id,
            stay_id=stay_id,
            cleanliness_rating=cleanliness_rating,
            staff_rating=staff_rating,
            food_rating=food_rating,
            service_rating=service_rating,
            comment=comment,
            overall_rating=overall_rating
        )

        db.session.add(feedback)
        db.session.flush()

        # Create department feedback records

        for item in validated_department_feedback:

            department_feedback = DepartmentFeedback(
                feedback_id=feedback.id,
                department_id=item["department_id"],
                rating=item["rating"],
                comment=item["comment"]
            )

            db.session.add(department_feedback)

        # Commit everything

        db.session.commit()

        # Send low-rating notification AFTER successful commit

        if overall_rating <= LOW_RATING_THRESHOLD:

            message = (
                f"Guest: {feedback.guest.name}\n"
                f"Overall Rating: {overall_rating}\n"
                f"Comment: {feedback.comment or 'No comment provided'}\n"
                f"Stay ID: {feedback.stay_id}"
            )

            notification_service.notify_admins(
                notification_type=LOW_RATING,
                title="Low Guest Rating Alert",
                message=message,
                alert_key=f"LOW_RATING-{feedback.id}"
            )

        return api_response(
            "success",
            200,
            "Feedback submitted successfully.",
            {
                "feedback": {
                    "id": feedback.id,
                    "overall_rating": feedback.overall_rating,
                    "cleanliness_rating": feedback.cleanliness_rating,
                    "staff_rating": feedback.staff_rating,
                    "food_rating": feedback.food_rating,
                    "service_rating": feedback.service_rating,
                    "guest_comment": feedback.comment,
                    "feedback_date": feedback.feedback_date
                }
            }
        )

    # Get all the feedbacks list function
    def get_feedbacks(self, rating_range=None, from_date=None, to_date=None):
        query = db.select(Feedback)
        
        # Filter by rating range
        if rating_range:
            try:
                min_rating, max_rating = map(
                    Decimal,
                    rating_range.split("-")
                )
            except (ValueError, AttributeError):
                return api_response(
                    "error",
                    400,
                    "Invalid rating range.",
                    {}
                )

            if min_rating < Decimal("0") or max_rating > Decimal("5"):
                return api_response(
                    "error",
                    400,
                    "Rating range must be between 0 and 5.",
                    {}
                )

            if min_rating >= max_rating:
                return api_response(
                    "error",
                    400,
                    "Invalid rating range.",
                    {}
                )

            if max_rating == Decimal("5"):
                query = query.where(
                    Feedback.overall_rating >= min_rating,
                    Feedback.overall_rating <= max_rating
                )
            else:
                query = query.where(
                    Feedback.overall_rating >= min_rating,
                    Feedback.overall_rating < max_rating
                )

        # Filter by from date
        if from_date:
            try:
                from_date = datetime.strptime(
                    from_date,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                return api_response(
                    "error",
                    400,
                    "Invalid from_date. Use YYYY-MM-DD format.",
                    {}
                )

            query = query.where(
                db.func.date(Feedback.feedback_date) >= from_date
            )

        # Filter by to date
        if to_date:
            try:
                to_date = datetime.strptime(
                    to_date,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                return api_response(
                    "error",
                    400,
                    "Invalid to_date. Use YYYY-MM-DD format.",
                    {}
                )

            query = query.where(
                db.func.date(Feedback.feedback_date) <= to_date
            )

        # Sort by newest feedback
        query = query.order_by(
            Feedback.feedback_date.desc()
        )

        # Execute query
        feedbacks = db.session.scalars(query).all()

        # Build response
        feedbacks_list = []

        for feedback in feedbacks:

            feedbacks_list.append({
                "id": feedback.id,
                "overall_rating": feedback.overall_rating,
                "cleanliness_rating": feedback.cleanliness_rating,
                "staff_rating": feedback.staff_rating,
                "food_rating": feedback.food_rating,
                "service_rating": feedback.service_rating,
                "guest_comment": feedback.comment,
                "feedback_date": feedback.feedback_date,

                "guest_details": {
                    "id": feedback.guest_id,
                    "guest_name": feedback.guest.name,
                    "guest_email": feedback.guest.email,

                    "stay_id": feedback.stay.id,
                    "stay_number": feedback.stay.stay_id,

                    "room_number": feedback.stay.room_number,
                    "room_type": feedback.stay.room_type,

                    "check_in_date": feedback.stay.check_in_date,
                    "check_out_date": feedback.stay.check_out_date
                }
            })

        return api_response(
            "success",
            200,
            "Feedbacks list fetched successfully.",
            {
                "feedbacks": feedbacks_list
            }
        )

    # Get specific feedback details function
    def get_feedback_details(self, feedback_id):
        feedback = db.session.get(Feedback, feedback_id)
        if not feedback:
            return api_response("error", 404, "Feedback does not exist.")

        return api_response("success", 200, "Feedback details retrieved successfully!", {
            "feedback":{
                "id": feedback.id,
                "overall_rating": feedback.overall_rating,
                "cleanliness_rating": feedback.cleanliness_rating,
                "staff_rating": feedback.staff_rating,
                "food_rating": feedback.food_rating,
                "service_rating": feedback.service_rating,
                "guest_comment": feedback.comment,
                "feedback_date": feedback.feedback_date,
                "guest_details":{
                    "id": feedback.guest_id,
                    "guest_name": feedback.guest.name,
                    "guest_email": feedback.guest.email,
                    "stay_id": feedback.stay.id,
                    "stay_number": feedback.stay.stay_id,
                    "room_number": feedback.stay.room_number,
                    "room_type": feedback.stay.room_type,
                    "check_in_date": feedback.stay.check_in_date,
                    "check_out_date": feedback.stay.check_out_date
                }
            }
        })