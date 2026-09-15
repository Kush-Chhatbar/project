import random
from decimal import Decimal, ROUND_HALF_UP

from app.extensions import db
from app.models.feedback import Feedback
from app.models.department import Department
from app.models.department_feedback import DepartmentFeedback


class DepartmentFeedbackSeeder:

    # ---------------------------------------------------------
    # Generate department-specific random rating
    # ---------------------------------------------------------

    @staticmethod
    def calculate_rating(department_name):
        """
        Generate a realistic department rating.

        Each department has its own rating profile so that
        department performance analytics produces meaningful
        results.
        """

        rating_profiles = {

            # Generally good
            "Housekeeping": [
                4.0,
                4.0,
                4.0,
                4.5,
                4.5,
                5.0
            ],

            # Generally needs improvement
            "Wi-fi": [
                1.5,
                2.0,
                2.0,
                2.5,
                3.0,
                3.0
            ],

            # Neutral / average
            "Maintenance": [
                2.5,
                3.0,
                3.0,
                3.5,
                3.5,
                4.0
            ],

            # Generally good
            "Food & Beverage": [
                3.5,
                4.0,
                4.0,
                4.5,
                4.5,
                5.0
            ],

            # Very good
            "Front Office": [
                4.0,
                4.0,
                4.5,
                4.5,
                5.0,
                5.0
            ],

            # Neutral / average
            "Finance & Billing": [
                2.5,
                3.0,
                3.0,
                3.5,
                3.5,
                4.0
            ],

            # Mixed performance
            "Guest Relations": [
                2.0,
                3.0,
                3.0,
                3.5,
                4.0,
                4.5
            ]
        }

        # Fallback for any future department
        ratings = rating_profiles.get(
            department_name,
            [
                1.0,
                2.0,
                2.5,
                3.0,
                3.5,
                4.0,
                4.5,
                5.0
            ]
        )

        rating = random.choice(ratings)

        return Decimal(str(rating)).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP
        )

    # ---------------------------------------------------------
    # Generate department-specific comment
    # ---------------------------------------------------------

    @staticmethod
    def generate_comment(department_name, rating):
        """
        Generate a comment based on the department rating.
        """

        rating = Decimal(str(rating))

        # Determine sentiment based on rating
        if rating >= Decimal("4.5"):
            sentiment = "positive"

        elif rating >= Decimal("3.0"):
            sentiment = "neutral"

        else:
            sentiment = "negative"

        comments = {

            "Housekeeping": {
                "positive": [
                    "The room was very clean and well maintained.",
                    "Housekeeping service was excellent.",
                    "The room was spotless and properly maintained.",
                    "Very satisfied with the cleanliness of the room."
                ],
                "neutral": [
                    "The room was reasonably clean, but some areas could be improved.",
                    "Housekeeping was satisfactory but could be more consistent.",
                    "The room was clean overall, although some improvements are needed."
                ],
                "negative": [
                    "The room cleanliness needs significant improvement.",
                    "The room was not cleaned properly.",
                    "There were cleanliness and maintenance issues in the room."
                ]
            },

            "Wi-fi": {
                "positive": [
                    "The Wi-fi connection was fast and reliable.",
                    "Wi-fi worked perfectly throughout the stay.",
                    "The internet connection was excellent.",
                    "Very good Wi-fi speed and connectivity."
                ],
                "neutral": [
                    "The Wi-fi worked reasonably well but was occasionally slow.",
                    "The internet connection was acceptable but could be improved.",
                    "Wi-fi worked most of the time but was inconsistent."
                ],
                "negative": [
                    "The Wi-fi connection was slow and unreliable.",
                    "Internet connectivity was poor during the stay.",
                    "The Wi-fi frequently disconnected.",
                    "The internet speed was not sufficient."
                ]
            },

            "Maintenance": {
                "positive": [
                    "The facilities were well maintained.",
                    "Maintenance service was quick and effective.",
                    "All facilities were in good working condition.",
                    "Maintenance issues were handled properly."
                ],
                "neutral": [
                    "Most facilities were fine, although some maintenance could be improved.",
                    "Maintenance was satisfactory but response time could be better.",
                    "There were a few minor maintenance issues."
                ],
                "negative": [
                    "Several maintenance issues need attention.",
                    "Some facilities were not working properly.",
                    "Maintenance response was slow.",
                    "The room had unresolved maintenance problems."
                ]
            },

            "Food & Beverage": {
                "positive": [
                    "The food quality was excellent and the service was good.",
                    "Food was delicious and served on time.",
                    "Very good food quality and restaurant service.",
                    "The dining experience was excellent."
                ],
                "neutral": [
                    "The food was satisfactory, although the service could be improved.",
                    "Food quality was average.",
                    "The food was acceptable but there is room for improvement.",
                    "Restaurant service was satisfactory but somewhat slow."
                ],
                "negative": [
                    "The food quality needs improvement.",
                    "The food was not satisfactory.",
                    "Restaurant service was slow and disappointing.",
                    "There were issues with the food and service."
                ]
            },

            "Front Office": {
                "positive": [
                    "The reception staff were helpful and professional.",
                    "Check-in and check-out were handled very efficiently.",
                    "The front office staff were friendly and welcoming.",
                    "Excellent service from the reception team."
                ],
                "neutral": [
                    "The reception experience was satisfactory but could be improved.",
                    "Check-in was acceptable but took longer than expected.",
                    "Front office service was generally good with minor delays."
                ],
                "negative": [
                    "The reception service needs improvement.",
                    "Check-in process was slow and inconvenient.",
                    "The front office staff were not very helpful.",
                    "There were issues during check-in and check-out."
                ]
            },

            "Finance & Billing": {
                "positive": [
                    "The billing and payment process was smooth.",
                    "The invoice was accurate and clearly explained.",
                    "Payment processing was quick and convenient.",
                    "The billing team handled everything professionally."
                ],
                "neutral": [
                    "The billing process was satisfactory but could be faster.",
                    "The invoice was mostly clear but some details needed explanation.",
                    "Payment processing was acceptable with minor delays."
                ],
                "negative": [
                    "There were issues with the billing and payment process.",
                    "The invoice contained discrepancies.",
                    "The billing process was confusing and took too long.",
                    "There was a problem with the payment calculation."
                ]
            },

            "Guest Relations": {
                "positive": [
                    "The staff were friendly and handled guest requests very well.",
                    "Guest relations provided excellent support.",
                    "The staff responded quickly to our concerns.",
                    "Very helpful and professional guest support."
                ],
                "neutral": [
                    "Guest support was satisfactory but could be improved.",
                    "The staff handled our requests reasonably well.",
                    "Guest relations service was acceptable but response time could improve."
                ],
                "negative": [
                    "The handling of guest requests needs improvement.",
                    "Our concerns were not addressed promptly.",
                    "Guest support was disappointing.",
                    "The response to our complaint was slower than expected."
                ]
            }
        }

        # Fallback comments
        default_comments = {
            "positive": [
                "Good experience with this department.",
                "The department provided excellent service."
            ],
            "neutral": [
                "The experience with this department was satisfactory.",
                "The service was acceptable but could be improved."
            ],
            "negative": [
                "The experience with this department needs improvement.",
                "The service provided by this department was disappointing."
            ]
        }

        department_comments = comments.get(
            department_name,
            default_comments
        )

        return random.choice(
            department_comments[sentiment]
        )

    # ---------------------------------------------------------
    # Seed department feedback
    # ---------------------------------------------------------

    @staticmethod
    def seed_department_feedback():

        try:

            # -------------------------------------------------
            # Get all feedback records
            # -------------------------------------------------

            feedbacks = (
                Feedback.query
                .order_by(Feedback.id)
                .all()
            )

            if not feedbacks:

                print("No feedback records found.")

                return

            # -------------------------------------------------
            # Get all active departments
            # -------------------------------------------------

            departments = (
                Department.query
                .filter_by(is_active=True)
                .order_by(Department.id)
                .all()
            )

            if not departments:

                print("No active departments found.")

                return

            # -------------------------------------------------
            # Existing department feedback
            #
            # This prevents duplicate records if the seeder
            # is executed multiple times.
            # -------------------------------------------------

            existing_records = {
                (
                    record.feedback_id,
                    record.department_id
                )
                for record in DepartmentFeedback.query.all()
            }

            created_count = 0
            skipped_count = 0

            # -------------------------------------------------
            # Create feedback for EVERY department
            # for EVERY feedback record
            # -------------------------------------------------

            for feedback in feedbacks:

                for department in departments:

                    key = (
                        feedback.id,
                        department.id
                    )

                    # Skip if this combination already exists
                    if key in existing_records:

                        skipped_count += 1

                        continue

                    # Generate random department rating
                    rating = (
                        DepartmentFeedbackSeeder.calculate_rating(
                            department.name
                        )
                    )

                    # Generate matching comment
                    comment = (
                        DepartmentFeedbackSeeder.generate_comment(
                            department.name,
                            rating
                        )
                    )

                    # Create department feedback
                    department_feedback = DepartmentFeedback(
                        feedback_id=feedback.id,
                        department_id=department.id,
                        rating=rating,
                        comment=comment
                    )

                    db.session.add(department_feedback)

                    existing_records.add(key)

                    created_count += 1

            # -------------------------------------------------
            # Commit
            # -------------------------------------------------

            db.session.commit()

            # -------------------------------------------------
            # Seeder summary
            # -------------------------------------------------

            expected_records = (
                len(feedbacks) * len(departments)
            )

            print()
            print("========================================")
            print("Department Feedback Seeder")
            print("========================================")
            print(
                f"Feedback records found : {len(feedbacks)}"
            )
            print(
                f"Departments found      : {len(departments)}"
            )
            print(
                f"Records created        : {created_count}"
            )
            print(
                f"Records skipped        : {skipped_count}"
            )
            print(
                f"Expected combinations : {expected_records}"
            )
            print("========================================")
            print()

        except Exception as e:

            db.session.rollback()

            print()
            print("========================================")
            print("Department Feedback Seeder ERROR")
            print("========================================")
            print(str(e))
            print("========================================")
            print()

            raise