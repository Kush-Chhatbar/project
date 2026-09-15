from app.extensions import db

class Stay(db.Model):
    __tablename__ = "stays"

    id = db.Column(db.Integer, primary_key=True)

    stay_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    guest_id = db.Column(
        db.Integer,
        db.ForeignKey("guests.id"),
        nullable=False
    )

    room_number = db.Column(db.String(20), nullable=False)

    room_type = db.Column(db.String(50), nullable=False)

    check_in_date = db.Column(db.Date, nullable=False)

    check_out_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    guest = db.relationship("Guest", backref="stays")