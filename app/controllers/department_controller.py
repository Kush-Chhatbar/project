from flask import request

from app.services.department_service import DepartmentService

class DepartmentController:
    def __init__(self):
        self.department_service = DepartmentService()

    # Get list of all departments
    def get_departments(self):
        return self.department_service.get_departments()

    # Get details of a specific department
    def get_department(self):
        department_id = request.args.get("department_id")
        return self.department_service.get_department_details(department_id)

    # Create a new department
    def create_department(self):
        data = request.get_json()
        return self.department_service.create_department(data)

    # Update department details
    def update_department(self):
        department_id = request.args.get("department_id")
        data = request.get_json()
        return self.department_service.update_department(department_id, data)

    # Delete a department
    def delete_department(self):
        department_id = request.args.get("department_id")
        return self.department_service.delete_department(department_id)

    # Activate a department
    def activate_department(self):
        department_id = request.args.get("department_id")
        return self.department_service.activate_department(department_id)