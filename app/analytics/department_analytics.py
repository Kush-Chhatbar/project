from app.extensions import db
from app.utils.response import api_response
from app.models.department import Department
from app.models.complaint import Complaint
from app.models.department_feedback import DepartmentFeedback


class DepartmentAnalytics:

    @staticmethod
    def get_department_performance():
        # Get all active departments
        departments = Department.query.filter_by(is_active=True).order_by(Department.id).all()

        if not departments:
            return {
                "departments": [],
                "most_complained_department": None,
                "highest_rated_department": None,
                "lowest_rated_department": None,
                "highest_sla_breach_department": None,
                "longest_resolution_department": None
            }

        # Complaint statistics
        complaints = Complaint.query.all()
        complaint_stats = {}
        for complaint in complaints:
            # Ignore complaints without a department
            if complaint.department_id is None:
                continue

            department_id = complaint.department_id

            if department_id not in complaint_stats:
                complaint_stats[department_id] = {
                    "complaints": 0,
                    "sla_breaches": 0,
                    "resolution_times": []
                }

            complaint_stats[department_id]["complaints"] += 1

            # SLA breach count
            if complaint.sla_status == "Breached":
                complaint_stats[department_id]["sla_breaches"] += 1

            # Resolution time
            if complaint.created_at is not None and complaint.resolved_at is not None:
                resolution_time = complaint.resolved_at - complaint.created_at
                resolution_hours = resolution_time.total_seconds() / 3600
                complaint_stats[department_id]["resolution_times"].append(resolution_hours)

        # Department feedback statistics
        department_feedbacks = DepartmentFeedback.query.all()

        rating_stats = {}

        for department_feedback in department_feedbacks:

            department_id = department_feedback.department_id

            if department_id not in rating_stats:
                rating_stats[department_id] = []

            rating_stats[department_id].append(
                float(department_feedback.rating)
            )

        # Build department performance

        department_performance = []
        for department in departments:
            department_id = department.id

            complaint_data = complaint_stats.get(
                department_id,
                {
                    "complaints": 0,
                    "sla_breaches": 0,
                    "resolution_times": []
                }
            )

            complaints_count = complaint_data["complaints"]
            sla_breaches = complaint_data["sla_breaches"]
            resolution_times = complaint_data[
                "resolution_times"
            ]

            if resolution_times:
                average_resolution_hours = (
                    sum(resolution_times)
                    / len(resolution_times)
                )
            else:
                average_resolution_hours = 0

            # Department rating
            ratings = rating_stats.get(department_id,[])
            if ratings:
                average_rating = sum(ratings)/ len(ratings)
            else:
                average_rating = 0

            # Add department result
            department_performance.append({
                "department": department.name,
                "complaints": complaints_count,
                "average_rating": round(
                    average_rating,
                    2
                ),
                "average_resolution_hours": round(
                    average_resolution_hours,
                    2
                ),
                "sla_breaches": sla_breaches
            })

        # Most complained-about department
        departments_with_complaints = [
            department
            for department in department_performance
            if department["complaints"] > 0
        ]

        if departments_with_complaints:
            most_complained_department = max(
                departments_with_complaints,
                key=lambda x: x["complaints"]
            )["department"]

        else:
            most_complained_department = None

        # Highest rated department
        departments_with_ratings = [
            department
            for department in department_performance
            if department["average_rating"] > 0
        ]

        if departments_with_ratings:
            highest_rated_department = max(
                departments_with_ratings,
                key=lambda x: x["average_rating"]
            )["department"]

            lowest_rated_department = min(
                departments_with_ratings,
                key=lambda x: x["average_rating"]
            )["department"]

        else:
            highest_rated_department = None
            lowest_rated_department = None

        # Highest SLA breach department
        departments_with_sla_breaches = [
            department
            for department in department_performance
            if department["sla_breaches"] > 0
        ]

        if departments_with_sla_breaches:
            highest_sla_breach_department = max(
                departments_with_sla_breaches,
                key=lambda x: x["sla_breaches"]
            )["department"]

        else:
            highest_sla_breach_department = None

        # Longest average resolution time
        departments_with_resolution = [
            department
            for department in department_performance
            if department["average_resolution_hours"] > 0
        ]

        if departments_with_resolution:
            longest_resolution_department = max(
                departments_with_resolution,
                key=lambda x: x["average_resolution_hours"]
            )["department"]

        else:
            longest_resolution_department = None

        data = {
            "departments": department_performance,

            "most_complained_department":
                most_complained_department,

            "highest_rated_department":
                highest_rated_department,

            "lowest_rated_department":
                lowest_rated_department,

            "highest_sla_breach_department":
                highest_sla_breach_department,

            "longest_resolution_department":
                longest_resolution_department
        } 

        return api_response("success", 200, "Department analytics are as below:", data)