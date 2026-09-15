from app.extensions import db
from app.factories import GuestFactory

def seed_guests():
    count = 40
    guests = GuestFactory.create_batch(count)

    db.session.add_all(guests)

    db.session.commit()

    print(f"{count} guests created.")