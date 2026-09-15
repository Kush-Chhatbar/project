from app.extensions import db
from app.factories.complaint_category_factory import ComplaintCategoryFactory

def seed_complaint_categories():

    categories = [
        {
            "name": "Housekeeping",
            "description": "Complaints related to room cleaning, housekeeping service, linens, towels, and room cleanliness."
        },
        {
            "name": "Maintenance",
            "description": "Complaints related to plumbing, electrical issues, air conditioning, appliances, and other maintenance problems."
        },
        {
            "name": "Restaurant",
            "description": "Complaints related to food quality, restaurant service, dining experience, and food delivery."
        },
        {
            "name": "Reception",
            "description": "Complaints related to front desk service, check-in, check-out, and reception assistance."
        },
        {
            "name": "Billing",
            "description": "Complaints related to incorrect charges, invoices, payments, refunds, and billing discrepancies."
        },
        {
            "name": "Wi-Fi",
            "description": "Complaints related to internet connectivity, Wi-Fi availability, speed, and access issues."
        },
        {
            "name": "Room",
            "description": "Complaints related to room condition, facilities, room allocation, noise, and overall room comfort."
        },
        {
            "name": "Staff Behaviour",
            "description": "Complaints related to staff conduct, communication, professionalism, courtesy, or inappropriate behaviour."
        },
        {
            "name": "Booking",
            "description": "Complaints related to reservations, booking modifications, cancellations, availability, and booking discrepancies."
        },
        {
            "name": "Other",
            "description": "Complaints that do not fall under any of the defined complaint categories."
        }
    ]

    complaint_categories = ComplaintCategoryFactory.create_batch(categories)

    db.session.add_all(complaint_categories)
    db.session.commit()

    print(f"{len(complaint_categories)} complaint categories created.")