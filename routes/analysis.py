from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.database import db
from backend.models.resume import Resume
from backend.models.report import AnalysisReport
from backend.services.jd_parser import extract_keywords_from_jd
from backend.services.matcher import compute_semantic_similarity
from backend.services.ats import calculate_ats_card
from backend.services.optimizer import generate_suggestions
from backend.services.interview import generate_interview_questions

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    data = request.get_json() or {}
    resume_id = data.get('resume_id')
    jd_text = data.get('jd_text')
    target_company = data.get('target_company', 'Target JD Match')
    
    if not resume_id or not jd_text:
        return jsonify({"error": "resume_id and jd_text are required"}), 400
        
    user_id = get_jwt_identity()
    
    # Retrieve resume
    resume = Resume.query.filter_by(id=resume_id, user_id=int(user_id)).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
        
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        # 1. Process JD and extract keywords
        jd_keywords = extract_keywords_from_jd(jd_text)
        
        # 2. Compute semantic similarity (hybrid embeddings)
        semantic_score = compute_semantic_similarity(resume.text_content, jd_text, api_key=api_key)
        
        # 3. Calculate full ATS report metrics (full text matching)
        metadata = resume.get_metadata()
        card_results = calculate_ats_card(metadata, resume.text_content, jd_keywords, jd_text, semantic_score)
        
        # 4. Generate suggestions
        suggestions = generate_suggestions(
            card_results["matched_skills"], 
            card_results["missing_skills"], 
            metadata, 
            api_key=api_key
        )
        
        # 5. Generate interview questions
        questions = generate_interview_questions(
            card_results["matched_skills"], 
            card_results["missing_skills"], 
            jd_text, 
            api_key=api_key
        )
        
        # 6. Save Analysis Report
        report = AnalysisReport(
            resume_id=resume.id,
            jd_text=jd_text,
            overall_score=card_results["scores"]["overall"]
        )
        
        # Save structural details inside the breakdown json
        report.set_breakdown({
            "target_company": target_company,
            "scores": card_results["scores"],
            "matched_categorized": card_results["matched_categorized"],
            "missing_categorized": card_results["missing_categorized"],
            "missing_resources": card_results["missing_resources"],
            "explanations": card_results["explanations"],
            "pass_probability": card_results["pass_probability"],
            "readability": card_results["readability"],
            "keyword_coverage": card_results["keyword_coverage"],
            "strengths": card_results["strengths"],
            "recruiter_feedback": card_results["recruiter_feedback"]
        })
        report.set_matched_skills(card_results["matched_skills"])
        report.set_missing_skills(card_results["missing_skills"])
        report.set_suggestions(suggestions)
        report.set_interview_questions(questions)
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error running analysis: {str(e)}"}), 500

@analysis_bp.route('/analysis/<int:report_id>', methods=['GET'])
@jwt_required()
def get_analysis(report_id):
    user_id = get_jwt_identity()
    report = AnalysisReport.query.join(Resume).filter(
        AnalysisReport.id == report_id,
        Resume.user_id == int(user_id)
    ).first()
    
    if not report:
        return jsonify({"error": "Report not found"}), 404
        
    return jsonify(report.to_dict()), 200

@analysis_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    reports = AnalysisReport.query.join(Resume).filter(
        Resume.user_id == int(user_id)
    ).order_by(AnalysisReport.created_at.desc()).all()
    
    return jsonify([r.to_dict() for r in reports]), 200
