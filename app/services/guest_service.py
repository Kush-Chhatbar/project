from app.utils.response import api_response
from werkzeug.security import check_password_hash

from app.models import Guest
from app.models import Stay
from flask_jwt_extended import create_access_token

from datetime import date


class GuestAuthService:

    # Login Guest
    def login(self, data):

        email = data.get("email")
        stay_id = data.get("stay_id")
        password = data.get("password")

        if not email or not stay_id or not password:
            return api_response(
                "error",
                400,
                "Email, stay ID and password are required."
            )

        email = email.strip().lower()
        stay_id = stay_id.strip()

        guest = Guest.query.filter_by(email=email).first()

        if not guest:
            return api_response(
                "error",
                401,
                "Invalid email, stay ID or password."
            )

        if not guest.is_active:
            return api_response(
                "error",
                403,
                "Guest account is inactive."
            )

        # Check password
        if not check_password_hash(guest.password, password):
            return api_response(
                "error",
                401,
                "Password does not match. Please enter correct password."
            )

        # Find stay
        stay = Stay.query.filter_by(
            stay_id=stay_id
        ).first()

        if not stay:
            return api_response(
                "error",
                401,
                "Please enter valid Stay ID."
            )

        # Make sure the stay belongs to this guest
        if stay.guest_id != guest.id:
            return api_response(
                "error",
                401,
                "Please enter valid email or password."
            )

        # Make sure the guest's check_out date has not been passed.
        if stay.check_out_date < date.today():
            return api_response(
                "error",
                403,
                "You have already checked out from this stay. Login is no longer available."
            )

        # Make sure the guest' check_in date is not too far.
        if stay.check_in_date > date.today():
            days_until_check_in = (stay.check_in_date - date.today()).days

            if days_until_check_in > 7:
                return api_response(
                    "error",
                    403,
                    "Guest login will be available 7 days before your check-in date."
                )
        # Create JWT
        access_token = create_access_token(
            identity=str(guest.id),
            additional_claims={
                "stay_id": stay.id,
                "stay_number": stay.stay_id
            }
        )

        return api_response(
            "success",
            200,
            f"Welcome {guest.name}!",
            {
                "guest": {
                    "id": guest.id,
                    "name": guest.name,
                    "email": guest.email
                },
                "stay": {
                    "id": stay.id,
                    "stay_id": stay.stay_id,
                    "room_number": stay.room_number,
                    "room_type": stay.room_type,
                    "check_in_date": stay.check_in_date,
                    "check_out_date": stay.check_out_date
                },
                "access_token": access_token
            }
        )