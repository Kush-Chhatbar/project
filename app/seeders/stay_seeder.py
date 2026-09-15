from app.extensions import db
from app.factories import StayFactory

def seed_stays():
    count=40
    stays = StayFactory.create_batch(count)

    db.session.add_all(stays)

    db.session.commit()

    print(f"{count} stays created.")
