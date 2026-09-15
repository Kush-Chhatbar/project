from app.extensions import db

class DepartmentFeedback(db.Model):
    __tablename__ = "department_feedbacks"

    id = db.Column(db.Integer, primary_key=True)

    feedback_id = db.Column(
        db.Integer,
        db.ForeignKey("feedbacks.id"),
        nullable=False,
        index=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
        index=True
    )

    rating = db.Column(
        db.Numeric(2, 1),
        nullable=False
    )

    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    # Relationships
    feedback = db.relationship(
        "Feedback",
        backref=db.backref(
            "department_feedbacks",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    department = db.relationship(
        "Department",
        backref=db.backref(
            "department_feedbacks",
            lazy=True
        )
    )

    def __repr__(self):
        return (
            f"<DepartmentFeedback "
            f"feedback_id={self.feedback_id} "
            f"department_id={self.department_id} "
            f"rating={self.rating}>"
        )