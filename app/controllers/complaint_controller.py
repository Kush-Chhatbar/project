from flask import request
from app.models import Complaint
from app.services.complaint_service import ComplaintService

class ComplaintController:

    def __init__(self):
        self.complaint_service = ComplaintService()

    # Add a new complaint by guest function
    def add_complaint(self):
        data = request.get_json()
        return self.complaint_service.create_complaint(data=data)

    # Get all the complaints list function
    def get_complaints(self):
        status = request.args.get("status")
        priority = request.args.get("priority")
        category_name = request.args.get("category_name")
        department = request.args.get("department")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")

        return self.complaint_service.get_complaints(status=status, priority=priority, category_name=category_name, department=department, from_date=from_date, to_date=to_date)

    # Get details of a particular complaint function
    def get_complaint(self):
        complaint_id = request.args.get("complaint_id")
        return self.complaint_service.get_complaint_details(complaint_id=complaint_id)

    # Update complaint details function
    def update_complaint(self):
        complaint_id = request.args.get("complaint_id")
        data = request.get_json()
        return self.complaint_service.update_complaint(complaint_id=complaint_id, data=data)

    # Assign complaint to staff function
    def assign_complaint(self):
        complaint_id = request.args.get("complaint_id")
        data = request.get_json()
        return self.complaint_service.assign_complaint(complaint_id=complaint_id, data=data)

    # Update status of the complaint function
    def update_complaint_status(self):
        complaint_id = request.args.get("complaint_id")
        data = request.get_json()
        return self.complaint_service.update_complaint_status(complaint_id=complaint_id, data=data)

    # Add resolution notes to the complaint function
    def add_resolution_notes(self):
        complaint_id = request.args.get("complaint_id")
        data = request.get_json()
        return self.complaint_service.add_resolution(complaint_id=complaint_id, data=data)