from app import create_app
from app.seeders.user_seerder import seed_users
from app.seeders.complaint_category_seeder import seed_complaint_categories
from app.seeders.guest_seeder import seed_guests
from app.seeders.stay_seeder import seed_stays
from app.seeders.sla_rule_seeder import seed_sla_rules
from app.seeders.department_seeder import seed_departments
from app.seeders.feedback_seeder import seed_feedbacks
from app.seeders.complaint_seeder import seed_complaints
from app.seeders.department_feedback_seeder import DepartmentFeedbackSeeder

app = create_app()
departmentFeedbacks = DepartmentFeedbackSeeder()


with app.app_context():
    # seed_users()
    # seed_complaint_categories()
    # seed_guests()
    # seed_stays()
    # seed_sla_rules()
    # seed_departments()
    # seed_feedbacks()
    # seed_complaints()
    departmentFeedbacks.seed_department_feedback()