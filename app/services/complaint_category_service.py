from app.extensions import db
from app.models.complaint_category import ComplaintCategory
from app.utils.response import api_response

class ComplaintCategoryService:
    # Get all complaint categories list function
    def get_complaint_categories(self):
        complaint_categories = ComplaintCategory.query.order_by(ComplaintCategory.name.asc()).all()
        complaint_categories_list = []
        for complaint_category in complaint_categories:
            complaint_categories_list.append({
                "id": complaint_category.id,
                "name": complaint_category.name,
                "description": complaint_category.description,
                "is_active": complaint_category.is_active
            })

        return api_response("success", 200, "Complaint categories retrieved successfully!", {
            "complaint_categories": complaint_categories_list
        })

    # Get details of a particular complaint category
    def get_complaint_category_details(self, complaint_category_id):
        complaint_category = db.session.get(ComplaintCategory, complaint_category_id)
        if not complaint_category:
            return api_response("error", 404, "Complaint category not found.")

        return api_response("success", 200, "Complaint category details retrieved successfully!", {
            "complaint_category":{
                "id": complaint_category.id,
                "name": complaint_category.name,
                "description": complaint_category.description,
                "is_active": complaint_category.is_active
            }
        })

    # Add a new complaint category
    def create_complaint_category(self, data):
        name = data.get("name")
        description = data.get("description")

        if not name:
            return api_response("error", 400, "Complaint category name is required.")

        name = name.strip()
        description = description.strip() if description else None

        existing_complaint_category = ComplaintCategory.query.filter_by(name=name).first()

        if existing_complaint_category:
            return api_response("error", 409, "Complaint category with this name already exists.")

        complaint_category = ComplaintCategory(name=name, description=description)

        db.session.add(complaint_category)
        db.session.commit()

        return api_response("success", 201, "Complaint category created successfully!", {
            "complaint_category": {
                "id": complaint_category.id,
                "name": complaint_category.name,
                "description": complaint_category.description,
                "is_active": complaint_category.is_active           
            }
        })

    # Update complaint category details function
    def update_complaint_category(self, complaint_category_id, data):
        complaint_category = db.session.get(ComplaintCategory, complaint_category_id)
        if not complaint_category:
            return api_response("error", 404, "Complaint category not found.")

        if "name" in data:
            name = data.get("name")
            if not name or not name.strip():
                return api_response("error", 400, "Complaint category name cannot be empty.")

            name = name.strip()
            existing_complaint_category =   ComplaintCategory.query.filter(
                                                ComplaintCategory.name == name, 
                                                ComplaintCategory.id != complaint_category_id
                                            ).first()

            if complaint_category:
                return api_response("error", 409, "Complaint category with this name already exists.")

            complaint_category.name = name

            if "description" in data:
                description = data.get("description")
                complaint_category.description = description.strip()

            db.session.commit()

            return api_response("success", 200, "Complaint category updated successfully!", {
                "complaint_category": {
                    "id": complaint_category.id,
                    "name": complaint_category.name, 
                    "description": complaint_category.description,
                    "is_active": complaint_category.is_active
                }
            })

    # Deactivate department function
    def deactivate_complaint_category(self, complaint_category_id):
        complaint_category = db.session.get(ComplaintCategory, complaint_category_id)
        if not complaint_category:
            return api_response("error", 404, "Complaint category not found.")

        if not complaint_category.is_active:
            return api_response("error", 400, "Complaint category is already inactive.")

        complaint_category.is_active = False

        db.session.commit()

        return api_response("success", 200, "Complaint category deleted successfully.")

    # Activate department function
    def activate_complaint_category(self, complaint_category_id):
        complaint_category = db.session.get(ComplaintCategory, complaint_category_id)
        if not complaint_category:
            return api_response("error", 404, "Complaint category not found.")

        if complaint_category.is_active:
            return api_response("error", 400, "Complaint category is already active.")

        complaint_category.is_active = True

        db.session.commit()

        return api_response("success", 200, "Complaint category activated successfully.")