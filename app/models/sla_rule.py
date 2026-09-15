from app.extensions import db

class SLARule(db.Model):
    __tablename__ = "sla_rules"

    id = db.Column(db.Integer, primary_key=True)

    priority = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    resolution_target_minutes = db.Column(
        db.Integer,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )