from datetime import datetime, timedelta
import random

from sqlalchemy import func

from app.extensions import db
from app.factories.complaint_factory import ComplaintFactory
from app.models.complaint import Complaint
from app.models.complaint_category import ComplaintCategory
from app.models.department import Department
from app.models.sla_rule import SLARule
from app.models.stay import Stay
from app.models.user import User
from app.models.guest import Guest

COMPLAINT_DATA = [

    # 1
    {
        "category": "Housekeeping",
        "department": "Housekeeping",
        "description": "Room was not cleaned properly.",
        "priority": "High",
        "status": "New",
        "sla": "within"
    },

    # 2
    {
        "category": "Maintenance",
        "department": "Maintenance",
        "description": "Air conditioning is not cooling properly.",
        "priority": "Critical",
        "status": "Assigned",
        "sla": "breached"
    },

    # 3
    {
        "category": "Restaurant",
        "department": "Food & Beverage",
        "description": "Restaurant order took too long to arrive.",
        "priority": "Medium",
        "status": "In Progress",
        "sla": "approaching"
    },

    # 4
    {
        "category": "Reception",
        "department": "Front Office",
        "description": "Check-in process took too long.",
        "priority": "Medium",
        "status": "Resolved",
        "sla": "within"
    },

    # 5
    {
        "category": "Billing",
        "department": "Finance & Billing",
        "description": "The final bill contains an incorrect charge.",
        "priority": "High",
        "status": "Closed",
        "sla": "breached"
    },

    # 6
    {
        "category": "Wi-Fi",
        "department": "Wi-Fi",
        "description": "Wi-Fi keeps disconnecting from the room.",
        "priority": "High",
        "status": "In Progress",
        "sla": "approaching"
    },

    # 7
    {
        "category": "Room",
        "department": "Housekeeping",
        "description": "Room amenities were missing.",
        "priority": "Low",
        "status": "Resolved",
        "sla": "within"
    },

    # 8
    {
        "category": "Staff Behaviour",
        "department": "Guest Relations",
        "description": "Staff member was not polite while handling a request.",
        "priority": "High",
        "status": "Assigned",
        "sla": "within"
    },

    # 9
    {
        "category": "Booking",
        "department": "Front Office",
        "description": "Booking details were not reflected correctly.",
        "priority": "Medium",
        "status": "Resolved",
        "sla": "within"
    },

    # 10
    {
        "category": "Other",
        "department": "Guest Relations",
        "description": "General guest service complaint.",
        "priority": "Low",
        "status": "New",
        "sla": "within"
    },

    # 11 - REPEAT
    {
        "category": "Housekeeping",
        "department": "Housekeeping",
        "description": "Room cleaning issue occurred again.",
        "priority": "High",
        "status": "In Progress",
        "sla": "breached",
        "repeat": True
    },

    # 12 - REPEAT
    {
        "category": "Maintenance",
        "department": "Maintenance",
        "description": "Air conditioning problem has occurred again.",
        "priority": "Critical",
        "status": "Resolved",
        "sla": "breached",
        "repeat": True
    },

    # 13 - REPEAT
    {
        "category": "Wi-Fi",
        "department": "Wi-Fi",
        "description": "Wi-Fi is still disconnecting frequently.",
        "priority": "Medium",
        "status": "Assigned",
        "sla": "approaching",
        "repeat": True
    },

    # 14 - REPEAT
    {
        "category": "Reception",
        "department": "Front Office",
        "description": "Reception response was slow again.",
        "priority": "Medium",
        "status": "Closed",
        "sla": "within",
        "repeat": True
    },

    # 15
    {
        "category": "Restaurant",
        "department": "Food & Beverage",
        "description": "Food was served cold.",
        "priority": "High",
        "status": "In Progress",
        "sla": "within"
    },

    # 16
    {
        "category": "Maintenance",
        "department": "Maintenance",
        "description": "Bathroom plumbing requires repair.",
        "priority": "Critical",
        "status": "Assigned",
        "sla": "breached"
    },

    # 17
    {
        "category": "Billing",
        "department": "Finance & Billing",
        "description": "Refund amount has not been processed correctly.",
        "priority": "Medium",
        "status": "Resolved",
        "sla": "within"
    },

    # 18 - REPEAT
    {
        "category": "Restaurant",
        "department": "Food & Beverage",
        "description": "Restaurant service was slow again.",
        "priority": "Medium",
        "status": "New",
        "sla": "within",
        "repeat": True
    },

    # 19
    {
        "category": "Room",
        "department": "Housekeeping",
        "description": "Room furniture was damaged.",
        "priority": "Low",
        "status": "Closed",
        "sla": "within"
    },

    # 20
    {
        "category": "Staff Behaviour",
        "department": "Guest Relations",
        "description": "Staff communication was not satisfactory.",
        "priority": "High",
        "status": "In Progress",
        "sla": "breached"
    },

    # 21 - REPEAT
    {
        "category": "Staff Behaviour",
        "department": "Guest Relations",
        "description": "Another staff behaviour issue was reported.",
        "priority": "Medium",
        "status": "Assigned",
        "sla": "within",
        "repeat": True
    },

    # 22
    {
        "category": "Booking",
        "department": "Front Office",
        "description": "The room type provided did not match the booking.",
        "priority": "High",
        "status": "Resolved",
        "sla": "within"
    },

    # 23
    {
        "category": "Wi-Fi",
        "department": "Wi-Fi",
        "description": "Internet speed is extremely slow.",
        "priority": "Low",
        "status": "New",
        "sla": "within"
    },

    # 24
    {
        "category": "Other",
        "department": "Guest Relations",
        "description": "Guest requested assistance with a general concern.",
        "priority": "Low",
        "status": "Closed",
        "sla": "within"
    }
]

def get_department(name):

    department = Department.query.filter(
        func.lower(Department.name) == name.lower()
    ).first()

    if not department and name == "Wi-Fi":

        department = Department.query.filter(
            func.lower(Department.name) == "wi-fi & it support"
        ).first()

    if not department:
        raise Exception(
            f"Department '{name}' not found. "
            f"Please seed departments first."
        )

    return department

def get_category(name):

    category = ComplaintCategory.query.filter(
        func.lower(ComplaintCategory.name) == name.lower()
    ).first()

    if not category:
        raise Exception(
            f"Complaint category '{name}' not found. "
            f"Please seed complaint categories first."
        )

    if hasattr(category, "is_active") and not category.is_active:
        raise Exception(
            f"Complaint category '{name}' is inactive."
        )

    return category

def get_sla_minutes(priority):

    rule = SLARule.query.filter(
        func.lower(SLARule.priority) == priority.lower(),
        SLARule.is_active.is_(True)
    ).first()

    if not rule:
        raise Exception(
            f"No active SLA rule found for priority "
            f"'{priority}'. Please seed SLA rules first."
        )

    return rule.resolution_target_minutes

def get_sla_due_at(priority, sla_type):

    now = datetime.now()

    sla_minutes = get_sla_minutes(priority)

    # Already breached
    if sla_type == "breached":
        return now - timedelta(minutes=60)

    # Approaching SLA
    if sla_type == "approaching":
        return now + timedelta(minutes=15)

    # Normal SLA
    return now + timedelta(minutes=sla_minutes)

def get_next_complaint_number(start_number):

    return f"CMP-{start_number:06d}"

def seed_complaints():

    minimum_check_in = datetime(2026, 9, 14)

    eligible_stays = Stay.query.filter(
        Stay.check_in_date >= minimum_check_in
    ).all()

    if not eligible_stays:
        raise Exception(
            "No eligible stays found with check-in date "
            "on or after 2026-09-14."
        )
    
    valid_stays = [
        stay
        for stay in eligible_stays
        if stay.guest_id is not None
    ]

    if not valid_stays:
        raise Exception(
            "No eligible stays with a valid guest found."
        )

    admin = User.query.filter(
        func.lower(User.role) == "admin"
    ).first()

    staff = User.query.filter(
        func.lower(User.role) == "staff"
    ).first()

    if not admin:
        raise Exception(
            "No admin user found. "
            "Seed/create an admin first."
        )

    if not staff:
        raise Exception(
            "No staff user found. "
            "Seed/create a staff first."
        )

    last_complaint = Complaint.query.order_by(
        Complaint.id.desc()
    ).first()

    if last_complaint:
        next_number = last_complaint.id + 1
    else:
        next_number = 1

    complaints = []
    histories = []

    selected_stays = []

    for index, data in enumerate(COMPLAINT_DATA):
        if data.get("repeat") and selected_stays:
            stay = random.choice(selected_stays)

        else:
            stay = random.choice(valid_stays)
            selected_stays.append(stay)

        guest = Guest.query.filter(
            Guest.id == stay.guest_id
        ).first()

        if not guest:
            raise Exception(
                f"Guest with ID {stay.guest_id} "
                f"not found for stay ID {stay.id}."
            )

        category = get_category(
            data["category"]
        )

        department = get_department(
            data["department"]
        )

        sla_due_at = get_sla_due_at(
            priority=data["priority"],
            sla_type=data["sla"]
        )

        complaint_number = get_next_complaint_number(
            next_number
        )

        next_number += 1

        complaint = ComplaintFactory.create(
            complaint_data=data,
            guest=guest,
            stay=stay,
            category=category,
            department=department,
            admin=admin,
            staff=staff,
            complaint_number=complaint_number,
            sla_due_at=sla_due_at
        )

        db.session.add(complaint)

        db.session.flush()

        complaint_histories = (
            ComplaintFactory.create_histories(
                complaint=complaint,
                department=department,
                admin=admin,
                staff=staff
            )
        )

        histories.extend(complaint_histories)
        complaints.append(complaint)

    db.session.add_all(histories)

    db.session.commit()

    print(
        f"Complaint seeder completed successfully. "
        f"{len(complaints)} complaints created."
    )

    print(
        f"{len(complaints)} complaints + "
        f"{len(histories)} complaint history records created."
    )

    return complaints