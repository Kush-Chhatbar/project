from app.extensions import db
from app.models.department import Department
from app.utils.response import api_response

class DepartmentService:
    # Add new department function
    def create_department(self, data):
        name = data.get("name")
        description = data.get("description")

        if not name:
            return api_response("error", 400, "Department name is required.")

        name = name.strip()
        description = description.strip() if description else None

        existing_department = Department.query.filter_by(name=name).first()

        if existing_department:
            return api_response("error", 409, "Department with this name already exists.")

        department = Department(name=name, description=description, is_active=True)

        db.session.add(department)
        db.session.commit()

        return api_response("success", 201, "Department created successfully.", {
            "department": {
                "id": department.id,
                "name": department.name,
                "description": department.description,
                "is_active": department.is_active
            }
        })

    # Get all departments list function
    def get_departments(self):
        departments = Department.query.order_by(Department.name.asc()).all()
        department_list = []
        for department in departments:
            department_list.append({
                "id":department.id,
                "name":department.name,
                "description":department.description,
                "is_active":department.is_active
            })

        return api_response("success", 200, "Departments retrieved successfully.", {
            "departments": department_list
        })

    # Get specific department details function
    def get_department_details(self, department_id):
        department = db.session.get(Department, department_id)
        if not department:
            return api_response("error", 404, "Department not found.")

        return api_response("success", 200, "Department details retrieved successfully.", {
            "department":{
                "id": department.id,
                "name": department.name,
                "description": department.description,
                "is_active": department.is_active
            }
        })

    # Update department details function
    def update_department_details(self, department_id, data):
        department = db.session.get(Department, department_id)
        if not department:
            return api_response("error", 404, "Department not found.")

        if "name" in data:
            name = data.get("name")
            if not name or not name.strip():
                return api_response("error", 400, "Department name cannot be empty.")

            name = name.strip()
            existing_department =   Department.query.filter(
                                        Department.name == name,
                                        Department.id != department_id
                                    ).first()
            if existing_department:
                return api_response("error", 409, "Department with this name already exists.")

            department.name = name

            if "description" in data:
                description = data.get("description")
                department.description = description.strip()

            db.session.commit()

            return api_response("success", 200, "Department updated successfully.", {
                "department": {
                    "id": department.id,
                    "name": department.name,
                    "description": department.description,
                    "is_active": department.is_active
                }
            })

    # Deactivate department function
    def deactivate_department(self, department_id):
        department = db.session.get(Department, department_id)
        if not department:
            return api_response("error", 404, "Department not found.")

        if not department.is_active:
            return api_response("error", 400, "Department is already inactive.")

        department.is_active = False

        db.session.commit()

        return api_response("success", 200, "Department deleted successfully.")

    # Activate department function
    def activate_department(self, department_id):
        department = db.session.get(Department, department_id)
        if not department:
            return api_response("error", 404, "Department not found.")

        if department.is_active:
            return api_response("error", 400, "Department is already active.")

        department.is_active = True

        db.session.commit()

        return api_response("success", 200, "Department activated successfully.")