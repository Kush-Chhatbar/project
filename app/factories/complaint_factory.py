from datetime import datetime, timedelta

from app.extensions import db
from app.models.complaint import Complaint
from app.models.complaint_history import ComplaintHistory


class ComplaintFactory:

    @staticmethod
    def create_history(
        complaint,
        action_type,
        old_value=None,
        new_value=None,
        description=None,
        changed_by=None
    ):
        return ComplaintHistory(
            complaint_id=complaint.id,
            action_type=action_type,
            old_value=old_value,
            new_value=new_value,
            description=description,
            changed_by=changed_by
        )

    @staticmethod
    def create(
        complaint_data,
        guest,
        stay,
        category,
        department,
        admin,
        staff,
        complaint_number,
        sla_due_at
    ):
        priority = complaint_data["priority"]
        status = complaint_data["status"]
        sla_type = complaint_data["sla"]

        assigned_staff_id = None
        assigned_by = None

        if status != "New":
            assigned_staff_id = staff.id
            assigned_by = admin.id

        resolved_at = None
        closed_at = None
        resolution_notes = None

        if status in ["Resolved", "Closed"]:
            resolved_at = datetime.now() - timedelta(minutes=30)

            resolution_notes = (
                "The complaint was investigated and the "
                "required corrective action was completed."
            )

        if status == "Closed":
            closed_at = datetime.now() - timedelta(minutes=10)

        if sla_type == "breached":
            sla_status = "Breached"

        elif sla_type == "approaching":
            sla_status = "Approaching"

        else:
            sla_status = "Within SLA"

        complaint = Complaint(
            complaint_number=complaint_number,
            guest_id=guest.id,
            stay_id=stay.id,
            category_id=category.id,
            description=complaint_data["description"],
            priority=priority,
            department_id=(
                department.id
                if status != "New"
                else None
            ),
            assigned_by=assigned_by,
            assigned_staff_id=assigned_staff_id,
            status=status,
            sla_due_at=sla_due_at,
            resolved_at=resolved_at,
            closed_at=closed_at,
            resolution_notes=resolution_notes,
            sla_status=sla_status
        )

        return complaint

    @staticmethod
    def create_histories(
        complaint,
        department,
        admin,
        staff
    ):
        """
        Create complaint history records based on
        the complaint's current status.
        """

        histories = []

        status = complaint.status

        histories.append(
            ComplaintFactory.create_history(
                complaint=complaint,
                action_type="Created",
                old_value=None,
                new_value="New",
                description="Complaint created by guest.",
                changed_by=None
            )
        )

        if status != "New":

            histories.append(
                ComplaintFactory.create_history(
                    complaint=complaint,
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
                    changed_by=admin.id
                )
            )

        if status in [
            "In Progress",
            "Resolved",
            "Closed"
        ]:

            histories.append(
                ComplaintFactory.create_history(
                    complaint=complaint,
                    action_type="Status Updated",
                    old_value="Assigned",
                    new_value="In Progress",
                    description=(
                        "Complaint status changed from "
                        "Assigned to In Progress."
                    ),
                    changed_by=staff.id
                )
            )

        if status in [
            "Resolved",
            "Closed"
        ]:

            histories.append(
                ComplaintFactory.create_history(
                    complaint=complaint,
                    action_type="Status Updated",
                    old_value="In Progress",
                    new_value="Resolved",
                    description=(
                        "Complaint resolved by assigned staff."
                    ),
                    changed_by=staff.id
                )
            )

            histories.append(
                ComplaintFactory.create_history(
                    complaint=complaint,
                    action_type="Resolution Added",
                    old_value=None,
                    new_value=complaint.resolution_notes,
                    description=(
                        "Resolution notes added to the complaint."
                    ),
                    changed_by=staff.id
                )
            )

        if status == "Closed":

            histories.append(
                ComplaintFactory.create_history(
                    complaint=complaint,
                    action_type="Status Updated",
                    old_value="Resolved",
                    new_value="Closed",
                    description=(
                        "Complaint closed after resolution."
                    ),
                    changed_by=staff.id
                )
            )

        return histories