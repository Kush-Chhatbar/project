from app.extensions import db

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)

    guest_id = db.Column(
        db.Integer,
        db.ForeignKey("guests.id"),
        nullable=False
    )

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey("stays.id"),
        nullable=False
    )

    overall_rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    cleanliness_rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    staff_rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    food_rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    service_rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    comment = db.Column(db.Text)

    feedback_date = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    guest = db.relationship("Guest", backref="feedbacks")
    stay = db.relationship("Stay", backref="feedbacks")