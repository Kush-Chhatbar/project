from faker import Faker
from werkzeug.security import generate_password_hash

from app.models.guest import Guest

fake = Faker()

class GuestFactory:

    @staticmethod
    def create():
        return Guest(
            name=fake.name(),
            email=fake.unique.email(),
            password = generate_password_hash("guest123"),
            phone = fake.numerify("##########"),
            is_active = True
        )

    @staticmethod
    def create_batch(count):
        guests = []

        for _ in range(count):
            guest = GuestFactory.create()
            guests.append(guest)

        return guests