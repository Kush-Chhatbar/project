from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from .models.token_blocklist import TokenBlocklist
from .routes.auth import auth_bp
from .routes.departments import departments_bp
from .routes.complaint_categories import complaint_categories_bp
from .routes.guests import guests_bp
from .routes.feedbacks import feedbacks_bp
from .routes.complaints import complaints_bp
from . import models
from app.scheduler import start_scheduler
import os

def create_app():
    app = Flask(__name__)

    app.json.sort_keys = False
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # JWT token blocklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):

        jti = jwt_payload["jti"]

        token = db.session.scalar(
            db.select(TokenBlocklist).filter_by(jti=jti)
        )

        return token is not None
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(complaint_categories_bp)
    app.register_blueprint(guests_bp)
    app.register_blueprint(feedbacks_bp)
    app.register_blueprint(complaints_bp)
    
    @app.route('/')
    def home():
        return {
            "message": "Hotel Guest Feedback and Complaint Management System API is running."
        }

    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_scheduler(app)
        
    return app