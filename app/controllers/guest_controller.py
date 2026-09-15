from app.services.guest_service import GuestAuthService
from flask import request

class GuestController:
    def __init__(self):
        self.guest_auth_service = GuestAuthService()

    # Login Guests
    def login_guests(self):
        data = request.get_json()
        return self.guest_auth_service.login(data)

    