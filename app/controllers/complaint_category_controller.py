from flask import request

from app.services.complaint_category_service import ComplaintCategoryService

class ComplaintCategoryController:

    def __init__(self):
        self.complaint_category_service = ComplaintCategoryService()

    # Get list of all complaint categories
    def get_complaint_categories(self):
        return self.complaint_category_service.get_complaint_categories()

    # Get details of a particular complaint category
    def get_complaint_category(self):
        complaint_category_id = request.args.get("complaint_category_id")
        return self.complaint_category_service.get_complaint_category_details(complaint_category_id)

    # Create a new complaint category
    def create_complaint_category(self):
        data = request.get_json()
        return self.complaint_category_service.create_complaint_category(data)

    # Update complaint category
    def update_complaint_category(self):
        complaint_category_id = request.args.get("complaint_category_id")
        data = request.get_json()
        return self.complaint_category_service.update_complaint_category(complaint_category_id, data)

    # Delete complaint category
    def delete_complaint_category(self):
        complaint_category_id = request.args.get("complaint_category_id")
        return self.complaint_category_service.delete_complaint_category(complaint_category_id)

    # Activate complaint category
    def activate_complaint_category(self):
        complaint_category_id = request.args.get("complaint_category_id")
        return self.complaint_category_service.activate_complaint_category(complaint_category_id)