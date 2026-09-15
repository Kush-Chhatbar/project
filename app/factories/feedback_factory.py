from decimal import Decimal, ROUND_HALF_UP

from app.models.feedback import Feedback


class FeedbackFactory:

    @staticmethod
    def calculate_overall(cleanliness, staff, food, service):
        overall = (
            Decimal(str(cleanliness))
            + Decimal(str(staff))
            + Decimal(str(food))
            + Decimal(str(service))
        ) / Decimal("4")

        return overall.quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP
        )

    @staticmethod
    def create(
        guest,
        stay,
        cleanliness,
        staff,
        food,
        service,
        comment,
        feedback_date
    ):
        overall = FeedbackFactory.calculate_overall(
            cleanliness,
            staff,
            food,
            service
        )

        return Feedback(
            guest_id=guest.id,
            stay_id=stay.id,
            overall_rating=overall,
            cleanliness_rating=Decimal(str(cleanliness)),
            staff_rating=Decimal(str(staff)),
            food_rating=Decimal(str(food)),
            service_rating=Decimal(str(service)),
            comment=comment,
            feedback_date=feedback_date,
            created_at=feedback_date
        )

    @staticmethod
    def create_batch(feedback_data):
        feedbacks = []

        for data in feedback_data:
            feedback = FeedbackFactory.create(
                guest=data["guest"],
                stay=data["stay"],
                cleanliness=data["cleanliness"],
                staff=data["staff"],
                food=data["food"],
                service=data["service"],
                comment=data["comment"],
                feedback_date=data["feedback_date"]
            )

            feedbacks.append(feedback)

        return feedbacks