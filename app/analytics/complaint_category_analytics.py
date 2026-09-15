from sqlalchemy import func

from app.extensions import db
from app.models.complaint import Complaint
from app.models.complaint_category import ComplaintCategory
from app.utils.response import api_response


class ComplaintCategoryAnalytics:

    @staticmethod
    def get_category_analytics():
        total_complaints = db.session.query(func.count(Complaint.id)).scalar()

        results = (db.session.query(ComplaintCategory.id,ComplaintCategory.name,func.count(Complaint.id).label("complaint_count"))
            .outerjoin(Complaint,Complaint.category_id == ComplaintCategory.id)
            .group_by(ComplaintCategory.id,ComplaintCategory.name)
            .order_by(func.count(Complaint.id).desc())
            .all()
        )

        categories = []
        for result in results:
            complaint_count = result.complaint_count
            if total_complaints > 0:
                percentage = (complaint_count/ total_complaints) * 100
            else:
                percentage = 0

            categories.append({
                "category": result.name,
                "complaints": complaint_count,
                "percentage": round(percentage,2)
            })

        if categories:
            max_complaints = max(category["complaints"] for category in categories)

            if max_complaints > 0:
                most_common_categories = [
                    category["category"]
                    for category in categories
                    if category["complaints"] == max_complaints
                ]
            else:
                most_common_categories = []

        else:
            most_common_categories = []

        data = {
            "total_complaints": total_complaints,
            "categories": categories,
            "most_common_categories": most_common_categories
        }

        return api_response("success", 200, "Complaint category analysis details are as:", data)