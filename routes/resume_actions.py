from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.database import db
from backend.models.resume import Resume
from backend.services.optimizer import rewrite_section
from backend.services.cover_letter import generate_cover_letter

resume_bp = Blueprint('resume_actions', __name__)

@resume_bp.route('/resume/optimize', methods=['POST'])
@jwt_required()
def optimize_resume():
    """
    Endpoint: POST /api/resume/optimize
    Allows section specific optimizations (Summary, Experience, Projects, Skills)
    """
    data = request.get_json() or {}
    section_name = data.get('section_name')
    section_content = data.get('section_content')
    missing_skills = data.get('missing_skills', [])
    jd_text = data.get('jd_text', "")
    
    if not section_name or not section_content:
        return jsonify({"error": "section_name and section_content are required"}), 400
        
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        rewritten_text = rewrite_section(
            section_name=section_name,
            section_content=section_content,
            missing_skills=missing_skills,
            jd_text=jd_text,
            api_key=api_key
        )
        return jsonify({
            "section_name": section_name,
            "original_content": section_content,
            "rewritten_content": rewritten_text
        }), 200
    except Exception as e:
        return jsonify({"error": f"Rewrite failed: {str(e)}"}), 500

@resume_bp.route('/cover-letter', methods=['POST'])
@jwt_required()
def create_cover_letter():
    """
    Endpoint: POST /api/cover-letter
    Generates cover letters using Resume context and target JD.
    """
    data = request.get_json() or {}
    resume_id = data.get('resume_id')
    jd_text = data.get('jd_text')
    
    if not resume_id or not jd_text:
        return jsonify({"error": "resume_id and jd_text are required"}), 400
        
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(id=resume_id, user_id=int(user_id)).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
        
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        metadata = resume.get_metadata()
        letter = generate_cover_letter(
            resume_metadata=metadata,
            resume_text=resume.text_content,
            jd_text=jd_text,
            api_key=api_key
        )
        return jsonify({"cover_letter": letter}), 200
    except Exception as e:
        return jsonify({"error": f"Cover letter generation failed: {str(e)}"}), 500
