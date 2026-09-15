from app.extensions import db
from app.models import Department


def seed_departments():

    departments = [
        {
            "name": "Maintenance",
            "description": (
                "Handles electrical, plumbing, air conditioning, furniture, "
                "fixtures, and other physical maintenance issues."
            )
        },
        {
            "name": "Food & Beverage",
            "description": (
                "Responsible for restaurant service, food quality, food orders, "
                "dining service, and restaurant-related guest complaints."
            )
        },
        {
            "name": "Front Office",
            "description": (
                "Handles reception services, check-in and check-out, room "
                "allocation, reservations, and general front-desk assistance."
            )
        },
        {
            "name": "Finance & Billing",
            "description": (
                "Handles invoices, payments, refunds, billing discrepancies, "
                "and other financial concerns."
            )
        },
        {
            "name": "Guest Relations",
            "description": (
                "Handles guest experience issues, staff behaviour complaints, "
                "general concerns, and complaints that do not clearly belong "
                "to another department."
            )
        }
    ]

    created_count = 0

    for department_data in departments:

        department = Department.query.filter_by(
            name=department_data["name"]
        ).first()

        if department:
            department.description = department_data["description"]

            if hasattr(department, "is_active"):
                department.is_active = True

        else:
            department = Department(
                name=department_data["name"],
                description=department_data["description"]
            )

            if hasattr(department, "is_active"):
                department.is_active = True

            db.session.add(department)
            created_count += 1

    db.session.commit()

    print(
        f"Departments seeded successfully. "
        f"{created_count} new departments created."
    )