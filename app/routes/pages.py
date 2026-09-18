from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@pages_bp.route("/")
def landing():
    return render_template("index.html")


@pages_bp.route("/login")
def login_page():
    return render_template("login.html")


@pages_bp.route("/guest/login")
def guest_login_page():
    return render_template("guest-login.html")


# ---------------------------------------------------------------------------
# Guest pages (session guarded client-side; backend APIs enforce authz)
# ---------------------------------------------------------------------------

@pages_bp.route("/guest/dashboard")
def guest_dashboard():
    return render_template("guest/dashboard.html")


@pages_bp.route("/guest/feedback")
def guest_feedback_form():
    return render_template("guest/feedback.html")


@pages_bp.route("/guest/my-feedback")
def guest_my_feedback():
    return render_template("guest/my-feedback.html")


@pages_bp.route("/guest/complaints")
def guest_complaint_form():
    return render_template("guest/complaints.html")


@pages_bp.route("/guest/my-complaints")
def guest_my_complaints():
    return render_template("guest/my-complaints.html")


# ---------------------------------------------------------------------------
# Staff pages
# ---------------------------------------------------------------------------

@pages_bp.route("/staff/dashboard")
def staff_dashboard():
    return render_template("staff/dashboard.html")


@pages_bp.route("/staff/complaints")
def staff_complaints():
    return render_template("staff/complaints.html")


# ---------------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------------

@pages_bp.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin/dashboard.html")


@pages_bp.route("/admin/feedbacks")
def admin_feedbacks():
    return render_template("admin/feedbacks.html")


@pages_bp.route("/admin/complaints")
def admin_complaints():
    return render_template("admin/complaints.html")


# ---------------------------------------------------------------------------
# Shared profile page (all roles)
# ---------------------------------------------------------------------------

@pages_bp.route("/profile")
def profile_page():
    return render_template("profile.html")
