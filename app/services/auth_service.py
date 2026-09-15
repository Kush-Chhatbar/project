from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from app.utils.response import api_response
from app.extensions import db
from app.models.user import User
from app.models.token_blocklist import TokenBlocklist

# Login user function
def login_user(email, password):
    if not email or not password:
        return api_response("error",400,"Email and password are required.")
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return api_response("error", 401, "Invalid email or password.")

    if not user.is_active:
        return api_response("error", 403, "Your account is inactive. Please contact the administrator.")

    if not check_password_hash(user.password, password):
        return api_response("error", 401, "Invalid password.")

    access_token = create_access_token(identity=str(user.id), additional_claims={
                        "email": user.email,
                        "role": user.role   
                    })

    return api_response(
        "success",
        200,
        f"Welcome {user.name}, you are a {user.role}.",
        {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department": user.department_id,
                "role": user.role
            }
        }
    )

# Get curreent user function
def get_current_user():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return api_response("error", 404, "User not found.")

    return api_response("success", 200, "Current user retrieved successfully.",{
       "user": {
           "id": user.id,
            "name": user.name,
            "email": user.email,
            "department": user.department_id,
            "role": user.role
       }
    })

# Logout user function
def logout_authenticated_user():
    jti = get_jwt()["jti"]

    token = TokenBlocklist(jti=jti)

    db.session.add(token)
    db.session.commit()

    return api_response("success", 200, "User logged out successfully.")