import random

from faker import Faker
from datetime import date, timedelta
from app.models.stay import Stay
from app.models.guest import Guest

fake = Faker()

class StayFactory:

    @staticmethod
    def create(guest):
        check_in_date = date.today()

        stay_duration = fake.random_int(min=1, max=30)

        check_out_date = check_in_date + timedelta(
            days=stay_duration
        )

        return Stay(
            stay_id=f"STAY-{fake.unique.random_number(digits=8)}",
            guest_id=guest.id,
            room_number=str(
                fake.random_int(min=101, max=599)
            ),
            room_type=fake.random_element(
                elements=[
                    "Standard",
                    "Deluxe",
                    "Suite",
                    "Executive"
                ]
            ),
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )

    @staticmethod
    def create_batch(count):
        guests = Guest.query.all()

        if not guests:
            raise Exception(
                "No guests found. Seed guests first."
            )
        stays = []

        for _ in range(count):
            guest = random.choice(guests)
            stay = StayFactory.create(guest)
            stays.append(stay)

        return stays