from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile
from backend.models.database import db
from backend.models.resume import Resume
from backend.services.resume_parser import parse_resume
from backend.services.jd_parser import extract_keywords_from_jd

parser_bp = Blueprint('parser', __name__)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def is_allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@parser_bp.route('/upload-resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not is_allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format. Use PDF, DOCX, or TXT"}), 400
        
    user_id = get_jwt_identity()
    
    # Save file to a temp location to parse
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
    try:
        os.close(fd)
        file.save(temp_path)
        
        # Get api key from config
        api_key = current_app.config.get('GEMINI_API_KEY')
        
        # Parse resume text and metadata
        raw_text, parsed_metadata = parse_resume(temp_path, api_key=api_key)
        
        # Create Resume record
        resume = Resume(
            user_id=int(user_id),
            filename=file.filename,
            text_content=raw_text
        )
        resume.set_metadata(parsed_metadata)
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            "message": "Resume uploaded and parsed successfully",
            "resume_id": resume.id,
            "filename": resume.filename,
            "metadata": parsed_metadata
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error parsing resume: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@parser_bp.route('/upload-jd', methods=['POST'])
@jwt_required()
def upload_jd():
    # JD can be uploaded either as raw text in json or as a file
    jd_text = ""
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and is_allowed_file(file.filename):
            fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
            try:
                os.close(fd)
                file.save(temp_path)
                from backend.services.resume_parser import extract_text
                jd_text = extract_text(temp_path)
            except Exception as e:
                return jsonify({"error": f"Failed to parse JD file: {str(e)}"}), 500
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    else:
        # Check json body
        data = request.get_json() or {}
        jd_text = data.get("text", "")
        
    if not jd_text.strip():
        return jsonify({"error": "No Job Description text or file provided"}), 400
        
    keywords = extract_keywords_from_jd(jd_text)
    
    return jsonify({
        "message": "JD processed successfully",
        "text": jd_text,
        "keywords": keywords
    }), 200
