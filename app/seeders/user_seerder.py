from app.extensions import db
from app.factories import UserFactory


def seed_users():

    # Create 3 Admin users
    admins = UserFactory.create_batch(
        3,
        "admin"
    )

    # Create 10 Staff users
    staff = UserFactory.create_batch(
        10,
        "staff"
    )

    # Add users to database session
    db.session.add_all(admins)
    db.session.add_all(staff)

    # Save everything
    db.session.commit()

    print("3 admin users created.")
    print("10 staff users created.")