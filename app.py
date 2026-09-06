import os
import sys
import types

# Ensure current and parent directories are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Ensure 'backend' module is always resolvable regardless of repo root layout on Render
if 'backend' not in sys.modules:
    try:
        import backend
    except ModuleNotFoundError:
        m = types.ModuleType('backend')
        m.__path__ = [current_dir]
        sys.modules['backend'] = m

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging

from backend.config import Config
from backend.models.database import db

# Import blueprints
from backend.routes.auth import auth_bp
from backend.routes.parser import parser_bp
from backend.routes.analysis import analysis_bp
from backend.routes.resume_actions import resume_bp
from backend.routes.interview import interview_bp
from backend.routes.report import report_bp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # JWT Setup
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Your token has expired. Please log in again."}), 401
        
    @jwt.invalid_token_loader
    def my_invalid_token_callback(error_string):
        return jsonify({"error": "Invalid token. Authorization failed."}), 401
        
    @jwt.unauthorized_loader
    def my_unauthorized_callback(error_string):
        return jsonify({"error": "Missing authorization token."}), 401
        
    # Database Initialization
    db.init_app(app)
    
    # Register blueprints (supports both /api/path and /path)
    blueprints = [auth_bp, parser_bp, analysis_bp, resume_bp, interview_bp, report_bp]
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix='/api', name=f"{bp.name}_api")
        app.register_blueprint(bp, url_prefix='')
    
    # Add root and health check endpoints
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({"message": "PRO-ALIGN API Server is running", "status": "online"}), 200

    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "database": "connected" if db.engine else "Not connected"}), 200
        
    # Create tables and seed demo accounts under application context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables initialized successfully.")
            
            # Seed demo accounts if they do not exist
            from backend.models.user import User
            demo_users = [
                {"username": "demouser", "email": "demo@proalign.com", "password": "Password123!"},
                {"username": "candidate", "email": "candidate@proalign.com", "password": "Password123!"},
                {"username": "recruiter", "email": "recruiter@proalign.com", "password": "Password123!"}
            ]
            for u in demo_users:
                existing = User.query.filter((User.email == u["email"]) | (User.username == u["username"])).first()
                if not existing:
                    user = User(username=u["username"], email=u["email"])
                    user.set_password(u["password"])
                    db.session.add(user)
            db.session.commit()
            logger.info("Demo users verified/seeded successfully.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating database tables or seeding demo users: {e}")
            
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
