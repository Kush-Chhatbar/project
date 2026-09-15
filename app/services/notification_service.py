from app.models import Notification
from app.extensions import db
from app.utils.response import api_response

from app.models import User

class NotificationService:

    # Create a new notification function.
    def create_notification(self, user_id, notification_type, title, message, alert_key, complaint_id=None):

        # Check if notification already exits.
        existing_notification = Notification.query.filter_by(alert_key=alert_key).first()

        if existing_notification:
            return None

        notification = Notification(
            user_id=user_id,
            complaint_id=complaint_id,
            notification_type=notification_type,
            title=title,
            message=message,
            alert_key=alert_key,
            is_read=False
        )

        db.session.add(notification)

        return notification

    # Get list of all the admins function.
    def get_all_admins(self):
        admins =  User.query.filter_by(
            role="admin"
        ).all()
        return admins

    # Notify a specific user
    def notify_user(self,user_id,notification_type,title,message,alert_key,complaint_id=None):
        return self.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            alert_key=alert_key,
            complaint_id=complaint_id
        )

    # Send notification to all the admins function.
    def notify_admins(self,notification_type,title,message,alert_key,complaint_id=None):
        admins = self.get_all_admins()
        notifications = []

        for admin in admins:
            user_alert_key = f"{alert_key}-USER-{admin.id}"

            notification = self.create_notification(
                user_id=admin.id,
                notification_type=notification_type,
                title=title,
                message=message,
                alert_key=user_alert_key,
                complaint_id=complaint_id
            )

            notifications.append(notification)

notification_service = NotificationService()