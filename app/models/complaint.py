from app.extensions import db

class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)

    complaint_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

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

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("complaint_categories.id"),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=True
    )

    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="New"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    sla_due_at = db.Column(
        db.DateTime,
        nullable=True
    )

    resolved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    closed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    resolution_notes = db.Column(
        db.Text,
        nullable=True
    )

    sla_status = db.Column(
        db.String(20),
        nullable=True
    )

    guest = db.relationship("Guest")

    stay = db.relationship("Stay")

    category = db.relationship("ComplaintCategory")

    department = db.relationship("Department")

    assigned_by_user = db.relationship(
        "User",
        foreign_keys=[assigned_by]
    )

    assigned_staff = db.relationship(
        "User",
        foreign_keys=[assigned_staff_id]
    )

    