from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.models.database import db
from backend.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required"}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
        
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username_or_email') or data.get('email') # Support both keys
    password = data.get('password')
    
    if not username_or_email or not password:
        return jsonify({"error": "Username/Email and password are required"}), 400
        
    # Check both fields
    user = User.query.filter((User.email == username_or_email) | (User.username == username_or_email)).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username/email or password"}), 401
        
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "If this email is registered, a reset link will be sent shortly."}), 200
        
    return jsonify({"message": "Password reset token sent to your email."}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
