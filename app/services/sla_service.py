from datetime import datetime

from app.extensions import db
from app.models import Complaint

from app.constants.notification_types import ( SLA_APPROACHING, SLA_BREACH )

from app.services.notification_service import ( notification_service )

class SLAService:
    SLA_WARNING_MINUTES = 30

    # Check all open complaints function.
    def monitor_open_complaints(self):
        complaints = Complaint.query.filter(Complaint.status.in_(["Assigned","In Progress"])).all()

        print(f"SLA MONITOR: Checking {len(complaints)} open complaints.")

        for complaint in complaints:
            self.check_complaint_sla(complaint)

        db.session.commit()

    # Check individual complaint sla's function.
    def check_complaint_sla(self, complaint):
        if not complaint.sla_due_at:
            return
        now = datetime.now()

        # SLA breached
        if now >= complaint.sla_due_at:
            if complaint.sla_status != "Breached":
                complaint.sla_status = "Breached"
                self.create_breach_alert(complaint)
            return

        # SLA Approaching
        remaining_seconds = (complaint.sla_due_at - now).total_seconds()
        remaining_minutes = (remaining_seconds / 60)

        if remaining_minutes < self.SLA_WARNING_MINUTES:
            self.crete_approaching_alert(complaint)
            complaint.sla_status = "Approaching"


    # SLA Approaching Alert function
    def create_approaching_alert(self, complaint):
        message = self.complaint_message(complaint)

        alert_key = (f"SLA_APPROACHING-{complaint.id}")

        # Notify assigned staff
        if complaint.assigned_staff_id:

            staff_alert_key = (f"{alert_key}-STAFF-{complaint.assigned_staff_id}")

            notification_service.create_notification(
                user_id=complaint.assigned_staff_id,
                notification_type=SLA_APPROACHING,
                title="SLA Approaching Alert",
                message=message,
                alert_key=staff_alert_key,
                complaint_id=complaint.id
            )

        # Notify admins
        notification_service.notify_admins(
            notification_type=SLA_APPROACHING,
            title="SLA Approaching Alert",
            message=message,
            alert_key=alert_key,
            complaint_id=complaint.id
        )


    # SLA Breach Alert function.
    def create_breach_alert(self, complaint):
        message = self.complaint_message(complaint)

        alert_key = (f"SLA_BREACH-{complaint.id}")

        # Notify assigned staff
        if complaint.assigned_staff_id:

            staff_alert_key = (f"{alert_key}-STAFF-{complaint.assigned_staff_id}")

            notification_service.create_notification(
                user_id=complaint.assigned_staff_id,
                notification_type=SLA_BREACH,
                title="SLA Breach Alert",
                message=message,
                alert_key=staff_alert_key,
                complaint_id=complaint.id
            )

        # Notify admins
        notification_service.notify_admins(
            notification_type=SLA_BREACH,
            title="SLA Breach Alert",
            message=message,
            alert_key=alert_key,
            complaint_id=complaint.id
        )

    # Complaint message content function.
    def complaint_message(self, complaint):

        department_name = (complaint.department.name if complaint.department else "Not Assigned")

        return (
            f"Complaint: {complaint.complaint_number}\n"
            f"Priority: {complaint.priority}\n"
            f"Department: {department_name}\n"
            f"Created: {complaint.created_at}\n"
            f"SLA Due: {complaint.sla_due_at}\n"
            f"Current Status: {complaint.status}"
        )


sla_service = SLAService()