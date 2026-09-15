from faker import Faker
from werkzeug.security import generate_password_hash

from app.models.user import User


fake = Faker()


class UserFactory:

    @staticmethod
    def create(role):
        return User(
            name=fake.name(),
            email=fake.unique.email(),
            password=generate_password_hash("password123"),
            role=role,
            is_active=True
        )

    @staticmethod
    def create_batch(count, role):
        users = []

        for _ in range(count):
            user = UserFactory.create(role)
            users.append(user)

        return users