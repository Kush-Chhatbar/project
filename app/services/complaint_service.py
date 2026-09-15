from app.extensions import db
from app.utils.response import api_response

from app.models import Complaint
from app.models import ComplaintCategory
from app.models import ComplaintHistory
from app.models import Stay
from app.models import SLARule
from app.models import Department
from app.models import User

from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.constants.notification_types import CRITICAL_COMPLAINT, COMPLAINT_ASSIGNED
from app.services.notification_service import notification_service

import uuid

class ComplaintService:

    # Add a new complaint function
    def create_complaint(self, data):

        # Get logged-in guest information
        claims = get_jwt()
        guest_id = get_jwt_identity()
        stay_id = claims.get("stay_id")

        # Get request data
        category_id = data.get("category_id")
        description = data.get("description")
        priority = data.get("priority", "Medium")

        # Validate required fields
        if not category_id:
            return api_response(
                "error",
                400,
                "Complaint category is required.",
                {}
            )

        if not description:
            return api_response(
                "error",
                400,
                "Complaint description is required.",
                {}
            )
        
        # Validate priority
        allowed_priorities = [
            "Critical",
            "High",
            "Medium",
            "Low"
        ]

        if priority not in allowed_priorities:
            return api_response(
                "error",
                400,
                "Invalid complaint priority.",
                {}
            )

        # Validate guest/stay
        stay = db.session.get(Stay, stay_id)

        if not stay:
            return api_response(
                "error",
                404,
                "Stay not found.",
                {}
            )
        
        if stay.guest_id != int(guest_id):
            return api_response(
                "error",
                403,
                "You are not authorized to create a complaint for this stay.",
                {}
            )

        # Validate category
        category = db.session.get(
            ComplaintCategory,
            category_id
        )

        if not category:
            return api_response(
                "error",
                404,
                "Complaint category not found.",
                {}
            )

        if not category.is_active:
            return api_response(
                "error",
                400,
                "Selected complaint category is inactive.",
                {}
            )
        
        # Calculate SLA
        sla_rule = SLARule.query.filter_by(
            priority=priority,
            is_active=True
        ).first()

        if not sla_rule:
            return api_response(
                "error",
                500,
                "SLA rule not configured for this priority.",
                {}
            )

        sla_due_at = datetime.now() + timedelta(
            minutes=sla_rule.resolution_target_minutes
        )

        complaint_number = f"CMP-{uuid.uuid4().hex[:8].upper()}"

        # Create Complaint
        try:
            complaint = Complaint(
                complaint_number=complaint_number,
                guest_id=guest_id,
                stay_id=stay_id,
                category_id=category_id,
                description=description,
                priority=priority,
                status="New",
                sla_due_at=sla_due_at,
                sla_status="Within SLA"
            )

            db.session.add(complaint)

            # Flush so complaint.id is generated
            db.session.flush()

            # Create Complaint History
            history = ComplaintHistory(
                complaint_id=complaint.id,
                action_type="Created",
                old_value=None,
                new_value="New",
                description="Complaint created successfully.",
                changed_by=None
            )

            db.session.add(history)

            # Commit both
            db.session.commit()

            # Add notification for critical complaint
            if complaint.priority == "Critical":
                message = (
                    f"Complaint: {complaint.complaint_number}\n"
                    f"Priority: {complaint.priority}\n"
                    f"Department: Not Assigned\n"
                    f"Created: {complaint.created_at}\n"
                    f"Status: {complaint.status}"
                )

                notification_service.notify_admins(
                    notification_type=CRITICAL_COMPLAINT,
                    title="Critical Complaint Alert",
                    message=message,
                    alert_key=f"CRITICAL_COMPLAINT-{complaint.id}",
                    complaint_id=complaint.id
                )

            # Response
            return api_response(
                "success",
                201,
                "Complaint created successfully.",
                {
                    "complaint": {
                        "id": complaint.id,
                        "complaint_number": complaint.complaint_number,
                        "description": complaint.description,
                        "priority": complaint.priority,
                        "status": complaint.status,
                        "sla_due_at": complaint.sla_due_at,
                        "sla_status": complaint.sla_status
                    }
                }
            )
        except Exception as e:
            db.session.rollback()

            print("ERROR CREATING COMPLAINT:", repr(e))

            return api_response(
                "error",
                500,
                str(e),
                {}
            )

    # Get list of all the complaints function
    def get_complaints(self, status=None, priority=None, category_name=None, department=None, from_date=None, to_date=None):
        query = db.select(Complaint)

        # STATUS FILTER
        if status:
            allowed_statuses = [
                "New",
                "Assigned",
                "In Progress",
                "Resolved",
                "Closed"
            ]

            if status not in allowed_statuses:
                return api_response(
                    "error",
                    400,
                    "Invalid complaint status.",
                    {}
                )

            query = query.where(
                Complaint.status == status
            )

        # PRIORITY FILTER
        if priority:
            allowed_priorities = [
                "Critical",
                "High",
                "Medium",
                "Low"
            ]

            if priority not in allowed_priorities:
                return api_response(
                    "error",
                    400,
                    "Invalid complaint priority.",
                    {}
                )

            query = query.where(
                Complaint.priority == priority
            )

        # CATEGORY FILTER
        if category_name:
            query = query.join(
                ComplaintCategory,
                Complaint.category_id == ComplaintCategory.id
            ).where(
                ComplaintCategory.name.ilike(category_name)
            )

            # DEPARTMENT FILTER
            if department:
                query = query.join(
                    Department,
                    Complaint.department_id == Department.id
                ).where(
                    Department.name.ilike(department)
                )

        # FROM DATE FILTER
        if from_date:
            try:
                from_date = datetime.strptime(
                    from_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                return api_response(
                    "error",
                    400,
                    "Invalid from_date format. Use YYYY-MM-DD.",
                    {}
                )

            query = query.where(
                Complaint.created_at >= from_date
            )

        # TO DATE FILTER
        if to_date:
            try:
                to_date = datetime.strptime(
                    to_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                return api_response(
                    "error",
                    400,
                    "Invalid to_date format. Use YYYY-MM-DD.",
                    {}
                )

            # Include the entire to_date
            query = query.where(
                Complaint.created_at < to_date.replace(
                    hour=23,
                    minute=59,
                    second=59,
                    microsecond=999999
                )
            )

        # DATE VALIDATION
        if from_date and to_date and from_date > to_date:
            return api_response(
                "error",
                400,
                "From date cannot be greater than To date.",
                {}
            )

        # ORDER BY
        query = query.order_by(
            Complaint.priority.asc()
        )


        # EXECUTE QUERY
        complaints = db.session.scalars(query).all()

        # RESPONSE
        complaint_list = []

        for complaint in complaints:

            complaint_list.append({
                "id": complaint.id,
                "complaint_number": complaint.complaint_number,

                "description": complaint.description,

                "priority": complaint.priority,
                "status": complaint.status,

                "sla_due_at": complaint.sla_due_at,
                "sla_status": complaint.sla_status,

                "created_at": complaint.created_at,
                "updated_at": complaint.updated_at,

                "resolved_at": complaint.resolved_at,
                "closed_at": complaint.closed_at,

                "resolution_notes": complaint.resolution_notes,

                "guest_details": {
                    "id": complaint.guest_id,
                    "name": complaint.guest.name,
                    "email": complaint.guest.email
                },

                "stay_details": {
                    "id": complaint.stay_id,
                    "stay_id": complaint.stay.stay_id,
                    "room_number": complaint.stay.room_number,
                    "room_type": complaint.stay.room_type,
                    "check_in_date": complaint.stay.check_in_date,
                    "check_out_date": complaint.stay.check_out_date
                },

                "category": {
                    "id": complaint.category_id,
                    "name": complaint.category.name
                },

                "department": {
                    "id": complaint.department_id,
                    "name": (
                        complaint.department.name
                        if complaint.department
                        else None
                    )
                }
            })

        return api_response(
            "success",
            200,
            "Complaints fetched successfully.",
            {
                "complaints": complaint_list,
                "count": len(complaint_list)
            }
        )

    # Get details of a specific complaint function
    def get_complaint_details(self, complaint_id):

        complaint = db.session.get(Complaint, complaint_id)

        if not complaint:
            return api_response(
                "error",
                404,
                "Complaint not found.",
                {}
            )

        return api_response(
            "success",
            200,
            "Complaint fetched successfully.",
            {
                "complaint": {
                    "id": complaint.id,
                    "complaint_number": complaint.complaint_number,

                    "description": complaint.description,

                    "priority": complaint.priority,
                    "status": complaint.status,

                    "sla_due_at": complaint.sla_due_at,
                    "sla_status": complaint.sla_status,

                    "created_at": complaint.created_at,
                    "updated_at": complaint.updated_at,

                    "resolved_at": complaint.resolved_at,
                    "closed_at": complaint.closed_at,

                    "resolution_notes": complaint.resolution_notes,

                    "guest_details": {
                        "id": complaint.guest_id,
                        "name": complaint.guest.name,
                        "email": complaint.guest.email
                    },

                    "stay_details": {
                        "id": complaint.stay_id,
                        "stay_id": complaint.stay.stay_id,
                        "room_number": complaint.stay.room_number,
                        "room_type": complaint.stay.room_type,
                        "check_in_date": complaint.stay.check_in_date,
                        "check_out_date": complaint.stay.check_out_date
                    },

                    "category": {
                        "id": complaint.category_id,
                        "name": complaint.category.name
                    },

                    "department": {
                        "id": complaint.department_id,
                        "name": (
                            complaint.department.name
                            if complaint.department
                            else None
                        )
                    },

                    "assigned_staff": {
                        "id": (
                            complaint.assigned_staff.id
                            if complaint.assigned_staff
                            else None
                        ),
                        "name": (
                            complaint.assigned_staff.name
                            if complaint.assigned_staff
                            else None
                        ),
                        "email": (
                            complaint.assigned_staff.email
                            if complaint.assigned_staff
                            else None
                        )
                    }
                }
            }
        )

    # Update complaint details function
    def update_complaint(self, complaint_id, data):

        complaint = db.session.get(Complaint, complaint_id)

        if not complaint:
            return api_response(
                "error",
                404,
                "Complaint not found.",
                {}
            )

        if complaint.status != "New" or complaint.assigned_staff_id is not None:
            return api_response(
                "error",
                400,
                "Complaint cannot be updated once it has been assigned.",
                {}
            )

        # User performing the update
        user_id = get_jwt_identity()

        history_records = []

        allowed_priorities = [
            "Critical",
            "High",
            "Medium",
            "Low"
        ]

        allowed_statuses = [
            "New",
            "Assigned",
            "In Progress",
            "Resolved",
            "Closed"
        ]

        try:
            if "description" in data:

                description = data.get("description")

                if not description:
                    return api_response(
                        "error",
                        400,
                        "Complaint description cannot be empty.",
                        {}
                    )

                if description != complaint.description:

                    old_value = complaint.description

                    complaint.description = description

                    history_records.append(
                        {
                            "action_type": "Description Updated",
                            "old_value": old_value,
                            "new_value": description,
                            "description": "Complaint description updated."
                        }
                    )

            if "priority" in data:

                priority = data.get("priority")

                if priority not in allowed_priorities:
                    return api_response(
                        "error",
                        400,
                        "Invalid complaint priority.",
                        {}
                    )

                if priority != complaint.priority:

                    old_priority = complaint.priority

                    complaint.priority = priority

                    # Get new SLA rule
                    sla_rule = SLARule.query.filter_by(
                        priority=priority,
                        is_active=True
                    ).first()

                    if not sla_rule:
                        return api_response(
                            "error",
                            500,
                            "SLA rule not configured for this priority.",
                            {}
                        )

                    # Recalculate SLA from current time
                    complaint.sla_due_at = (
                        datetime.now()
                        + timedelta(
                            minutes=sla_rule.resolution_target_minutes
                        )
                    )

                    complaint.sla_status = "Within SLA"

                    history_records.append(
                        {
                            "action_type": "Priority Updated",
                            "old_value": old_priority,
                            "new_value": priority,
                            "description": (
                                f"Complaint priority changed "
                                f"from {old_priority} to {priority}."
                            )
                        }
                    )

            if "category_id" in data:

                category_id = data.get("category_id")

                category = db.session.get(
                    ComplaintCategory,
                    category_id
                )

                if not category:
                    return api_response(
                        "error",
                        404,
                        "Complaint category not found.",
                        {}
                    )

                if not category.is_active:
                    return api_response(
                        "error",
                        400,
                        "Selected complaint category is inactive.",
                        {}
                    )

                if category_id != complaint.category_id:

                    old_category = complaint.category.name

                    complaint.category_id = category_id

                    history_records.append(
                        {
                            "action_type": "Category Updated",
                            "old_value": old_category,
                            "new_value": category.name,
                            "description": (
                                f"Complaint category changed "
                                f"from {old_category} to {category.name}."
                            )
                        }
                    )

            if "department_id" in data:

                department_id = data.get("department_id")

                department = db.session.get(
                    Department,
                    department_id
                )

                if not department:
                    return api_response(
                        "error",
                        404,
                        "Department not found.",
                        {}
                    )

                if department_id != complaint.department_id:

                    old_department = (
                        complaint.department.name
                        if complaint.department
                        else None
                    )

                    complaint.department_id = department_id

                    history_records.append(
                        {
                            "action_type": "Department Updated",
                            "old_value": old_department,
                            "new_value": department.name,
                            "description": (
                                f"Complaint department changed "
                                f"from {old_department} to {department.name}."
                            )
                        }
                    )

            if "assigned_staff_id" in data:

                assigned_staff_id = data.get(
                    "assigned_staff_id"
                )

                staff = db.session.get(
                    User,
                    assigned_staff_id
                )

                if not staff:
                    return api_response(
                        "error",
                        404,
                        "Assigned staff member not found.",
                        {}
                    )

                if assigned_staff_id != complaint.assigned_staff_id:

                    old_staff = (
                        complaint.assigned_staff.name
                        if complaint.assigned_staff
                        else None
                    )

                    complaint.assigned_staff_id = assigned_staff_id

                    # If assigning staff, change status to Assigned
                    if complaint.status == "New":
                        complaint.status = "Assigned"

                    history_records.append(
                        {
                            "action_type": "Staff Assigned",
                            "old_value": old_staff,
                            "new_value": staff.name,
                            "description": (
                                f"Complaint assigned to {staff.name}."
                            )
                        }
                    )

            if "status" in data:

                status = data.get("status")

                if status not in allowed_statuses:
                    return api_response(
                        "error",
                        400,
                        "Invalid complaint status.",
                        {}
                    )

                if status != complaint.status:
                    old_status = complaint.status
                    complaint.status = status

                    if status == "Resolved":

                        complaint.resolved_at = datetime.now()

                        if not complaint.resolution_notes:
                            return api_response(
                                "error",
                                400,
                                "Resolution notes are required "
                                "when resolving a complaint.",
                                {}
                            )

                    elif status == "Closed":

                        if not complaint.resolved_at:
                            return api_response(
                                "error",
                                400,
                                "Complaint must be resolved before "
                                "it can be closed.",
                                {}
                            )

                        complaint.closed_at = datetime.now()

                    elif status in [
                        "New",
                        "Assigned",
                        "In Progress"
                    ]:

                        complaint.resolved_at = None
                        complaint.closed_at = None

                    history_records.append(
                        {
                            "action_type": "Status Updated",
                            "old_value": old_status,
                            "new_value": status,
                            "description": (
                                f"Complaint status changed "
                                f"from {old_status} to {status}."
                            )
                        }
                    )

            if "resolution_notes" in data:

                resolution_notes = data.get(
                    "resolution_notes"
                )

                if (
                    resolution_notes
                    != complaint.resolution_notes
                ):

                    old_notes = complaint.resolution_notes

                    complaint.resolution_notes = resolution_notes

                    history_records.append(
                        {
                            "action_type": "Resolution Notes Updated",
                            "old_value": old_notes,
                            "new_value": resolution_notes,
                            "description": "Resolution notes updated."
                        }
                    )

            # If complaint is not resolved/closed,
            # determine whether SLA has been breached.

            if complaint.status not in ["Resolved", "Closed"]:

                if (
                    complaint.sla_due_at
                    and datetime.now() > complaint.sla_due_at
                ):
                    complaint.sla_status = "Breached"
                else:
                    complaint.sla_status = "Within SLA"

            for record in history_records:

                history = ComplaintHistory(
                    complaint_id=complaint.id,
                    action_type=record["action_type"],
                    old_value=(
                        str(record["old_value"])
                        if record["old_value"] is not None
                        else None
                    ),
                    new_value=(
                        str(record["new_value"])
                        if record["new_value"] is not None
                        else None
                    ),
                    description=record["description"],
                    changed_by=user_id
                )

                db.session.add(history)

            db.session.commit()

            return api_response(
                "success",
                200,
                "Complaint updated successfully.",
                {
                    "complaint": {
                        "id": complaint.id,
                        "complaint_number": complaint.complaint_number,
                        "priority": complaint.priority,
                        "status": complaint.status,
                        "sla_due_at": complaint.sla_due_at,
                        "sla_status": complaint.sla_status,
                        "updated_at": complaint.updated_at
                    }
                }
            )

        except Exception as e:
            db.session.rollback()
            print(
                "ERROR UPDATING COMPLAINT:",
                repr(e)
            )
            return api_response(
                "error",
                500,
                "Failed to update complaint.",
                {}
            )

    # Assign complaint to a staff function
    def assign_complaint(self, complaint_id, data):
        complaint = db.session.get(Complaint, complaint_id)

        if not complaint:
            return api_response(
                "error",
                404,
                "Complaint not found.",
                {}
            )
        
        if complaint.status != "New":
            return api_response(
                "error",
                400,
                "Only new complaints can be assigned.",
                {}
            )
        
        if complaint.assigned_staff_id is not None:
            return api_response(
                "error",
                400,
                "Complaint has already been assigned.",
                {}
            )

        department_id = data.get("department_id")
        assigned_staff_id = data.get("assigned_staff_id")

        if not department_id:
            return api_response(
                "error",
                400,
                "Department is required.",
                {}
            )

        if not assigned_staff_id:
            return api_response(
                "error",
                400,
                "Staff member is required.",
                {}
            )

        admin_id = get_jwt_identity()

        try:
            department = db.session.get(
                Department,
                department_id
            )

            if not department:
                return api_response(
                    "error",
                    404,
                    "Department not found.",
                    {}
                )

            # If department is not deleted or is not made inactive
            if hasattr(department, "is_active") and not department.is_active:
                return api_response(
                    "error",
                    400,
                    "Selected department is inactive.",
                    {}
                )
            
            staff = db.session.get(
                User,
                assigned_staff_id
            )

            if not staff:
                return api_response(
                    "error",
                    404,
                    "Staff member not found.",
                    {}
                )

            # Make sure selected user is actually staff
            if staff.role != "staff":
                return api_response(
                    "error",
                    400,
                    "Selected user is not a staff member.",
                    {}
                )
            
            complaint.department_id = department_id
            complaint.assigned_staff_id = assigned_staff_id
            complaint.assigned_by = admin_id
            complaint.status = "Assigned"

            history = ComplaintHistory(
                complaint_id=complaint.id,
                action_type="Assigned",

                old_value="Department: None, Staff: None",

                new_value=(
                    f"Department: {department.name}, "
                    f"Staff: {staff.name}"
                ),

                description=(
                    f"Complaint assigned to {staff.name} "
                    f"under {department.name} department."
                ),

                changed_by=admin_id
            )

            db.session.add(history)

            # Notify the staff member when the complaint is assigned to them.
            message = (
                f"Complaint: {complaint.complaint_number}\n"
                f"Priority: {complaint.priority}\n"
                f"Department: {department.name}\n"
                f"Created: {complaint.created_at}\n"
                f"SLA Due: {complaint.sla_due_at}\n"
                f"Status: {complaint.status}"
            )

            notification_service.notify_user(
                user_id=staff.id,
                notification_type=COMPLAINT_ASSIGNED,
                title=f"New Complaint with {complaint.priority} priority has been Assigned",
                message=message,
                alert_key=f"COMPLAINT_ASSIGNED-{complaint.id}-STAFF-{staff.id}",
                complaint_id=complaint.id
            )

            db.session.commit()

            return api_response(
                "success",
                200,
                "Complaint assigned successfully.",
                {
                    "complaint": {
                        "id": complaint.id,
                        "complaint_number": complaint.complaint_number,
                        "status": complaint.status,

                        "department": {
                            "id": department.id,
                            "name": department.name
                        },

                        "assigned_staff": {
                            "id": staff.id,
                            "name": staff.name,
                            "email": staff.email
                        },

                        "assigned_by": admin_id
                    }
                }
            )

        except Exception as e:

            db.session.rollback()
            print(
                "ERROR ASSIGNING COMPLAINT:",
                repr(e)
            )
            return api_response(
                "error",
                500,
                "Failed to assign complaint.",
                {}
            )

    # Update status of the complaint function
    def update_complaint_status(self, complaint_id, data):
        complaint = db.session.get(Complaint, complaint_id)

        if not complaint:
            return api_response("error", 404, "Complaint not found.", {})

        status = data.get("status")

        if not status:
            return api_response(
                "error",
                400,
                "Complaint status is required.",
                {}
            )

        allowed_statuses = [
            "In Progress",
            "Resolved",
            "Closed"
        ]

        if status not in allowed_statuses:
            return api_response(
                "error",
                400,
                "Invalid complaint status.",
                {}
            )

        if complaint.assigned_staff_id is None:
            return api_response(
                "error",
                400,
                "Complaint must be assigned before its status can be updated.",
                {}
            )

        current_status = complaint.status

        if current_status == status:
            return api_response(
                "error",
                400,
                f"Complaint is already in '{status}' status.",
                {}
            )

        valid_transitions = {
            "Assigned": ["In Progress"],
            "In Progress": ["Resolved"],
            "Resolved": ["Closed"]
        }

        allowed_next_statuses = valid_transitions.get(
            current_status,
            []
        )

        if status not in allowed_next_statuses:
            return api_response(
                "error",
                400,
                (
                    f"Complaint cannot be moved from "
                    f"'{current_status}' to '{status}'."
                ),
                {}
            )

        user_id = get_jwt_identity()
        try:
            complaint.status = status

            if status == "Resolved":
                if not complaint.resolution_notes:
                    return api_response(
                        "error",
                        400,
                        "Resolution note must be added before resolving the complaint.",
                        {}
                    )

                complaint.resolved_at = datetime.now()

            elif status == "Closed":
                if not complaint.resolved_at:
                    return api_response(
                        "error",
                        400,
                        "Complaint must be resolved before it can be closed.",
                        {}
                    )

                complaint.closed_at = datetime.now()

            history = ComplaintHistory(
                complaint_id=complaint.id,
                action_type="Status Updated",
                old_value=current_status,
                new_value=status,
                description=(
                    f"Complaint status changed from "
                    f"{current_status} to {status}."
                ),
                changed_by=user_id
            )

            db.session.add(history)

            db.session.commit()

            return api_response(
                "success",
                200,
                "Complaint status updated successfully.",
                {
                    "complaint": {
                        "id": complaint.id,
                        "complaint_number": complaint.complaint_number,
                        "status": complaint.status,
                        "resolved_at": complaint.resolved_at,
                        "closed_at": complaint.closed_at,
                        "updated_at": complaint.updated_at
                    }
                }
            )
        
        except Exception as e:
            db.session.rollback()
            print(
                "ERROR UPDATING COMPLAINT STATUS:",
                repr(e)
            )
            return api_response(
                "error",
                500,
                "Failed to update complaint status.",
                {}
            )

    # Add resolution note while solving a complaint function
    def add_resolution(self, complaint_id, data):
        complaint = db.session.get(Complaint, complaint_id)

        if not complaint:
            return api_response(
                "error",
                404,
                "Complaint not found.",
                {}
            )

        resolution_notes = data.get("resolution_notes")

        if not resolution_notes:
            return api_response(
                "error",
                400,
                "Resolution notes are required.",
                {}
            )

        if complaint.assigned_staff_id is None:
            return api_response(
                "error",
                400,
                "Complaint must be assigned before adding a resolution.",
                {}
            )

        if complaint.status == "Closed":
            return api_response(
                "error",
                400,
                "Resolution cannot be updated after the complaint is closed.",
                {}
            )

        if complaint.status not in [
            "Assigned",
            "In Progress",
            "Resolved"
        ]:
            return api_response(
                "error",
                400,
                "Resolution cannot be added in the current complaint status.",
                {}
            )


        user_id = get_jwt_identity()

        try:
            old_resolution = complaint.resolution_notes
            complaint.resolution_notes = resolution_notes
            
            history = ComplaintHistory(
                complaint_id=complaint.id,
                action_type="Resolution Added",
                old_value=old_resolution,
                new_value=resolution_notes,
                description="Complaint resolution notes added/updated.",
                changed_by=user_id
            )

            db.session.add(history)
            db.session.commit()

            return api_response(
                "success",
                200,
                "Complaint resolution added successfully.",
                {
                    "complaint": {
                        "id": complaint.id,
                        "complaint_number": complaint.complaint_number,
                        "status": complaint.status,
                        "resolution_notes": complaint.resolution_notes,
                        "updated_at": complaint.updated_at
                    }
                }
            )

        except Exception as e:
            db.session.rollback()
            print(
                "ERROR ADDING COMPLAINT RESOLUTION:",
                repr(e)
            )
            return api_response(
                "error",
                500,
                "Failed to add complaint resolution.",
                {}
            )

        