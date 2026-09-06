import os
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
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(parser_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(resume_bp, url_prefix='/api')
    app.register_blueprint(interview_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/api')
    
    # Add root health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "database": str(db.engine.url if db.engine else "Not connected")}), 200
        
    # Create tables under application context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
